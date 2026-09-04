// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.19;

import {Test} from "forge-std/Test.sol";

import {MarketParams, Id} from "morpho-blue/src/interfaces/IMorpho.sol";
import {Morpho} from "morpho-blue/src/Morpho.sol";
import {ERC20Mock} from "morpho-blue/src/mocks/ERC20Mock.sol";
import {OracleMock} from "morpho-blue/src/mocks/OracleMock.sol";
import {IrmMock} from "morpho-blue/src/mocks/IrmMock.sol";
import {MarketParamsLib} from "morpho-blue/src/libraries/MarketParamsLib.sol";
import {MathLib} from "morpho-blue/src/libraries/MathLib.sol";
import {SharesMathLib} from "morpho-blue/src/libraries/SharesMathLib.sol";

/// @dev Handler-based invariant fuzz for the nutUSD market shape:
/// LLTV 38.5%, 18/18-dec mock tokens, controllable oracle, util-APR mock IRM.
contract NutHandler is Test {
    using MarketParamsLib for MarketParams;
    using MathLib for uint256;
    using SharesMathLib for uint256;

    Morpho public immutable morpho;
    ERC20Mock public immutable loan;
    ERC20Mock public immutable collateralToken;
    OracleMock public immutable oracle;
    address public immutable owner;

    MarketParams public marketParams;
    Id public id;

    address[4] public actors;
    address internal currentActor;

    uint256 public constant ORACLE_SCALE = 1e36;
    uint256 public constant WAD = 1e18;

    // ghosts
    uint256 public healthyLiquidations;
    uint256 public successfulLiquidations;
    uint256 public maxLifRatioWad;

    constructor(
        Morpho _morpho,
        ERC20Mock _loan,
        ERC20Mock _collateralToken,
        OracleMock _oracle,
        address _owner,
        MarketParams memory _marketParams
    ) {
        morpho = _morpho;
        loan = _loan;
        collateralToken = _collateralToken;
        oracle = _oracle;
        owner = _owner;
        marketParams = _marketParams;
        id = _marketParams.id();

        actors = [makeAddr("actor0"), makeAddr("actor1"), makeAddr("actor2"), makeAddr("actor3")];
        for (uint256 i; i < 4; ++i) {
            loan.setBalance(actors[i], 1e30);
            collateralToken.setBalance(actors[i], 1e30);
            vm.startPrank(actors[i]);
            loan.approve(address(morpho), type(uint256).max);
            collateralToken.approve(address(morpho), type(uint256).max);
            vm.stopPrank();
        }
    }

    modifier asActor(uint256 seed) {
        currentActor = actors[seed % 4];
        vm.startPrank(currentActor);
        _;
        vm.stopPrank();
    }

    function _pos(address user) internal view returns (uint256, uint128, uint128) {
        return morpho.position(id, user);
    }

    /* HANDLERS */

    function supply(uint256 assets, uint256 seed) public asActor(seed) {
        assets = bound(assets, 1, 1e24);
        morpho.supply(marketParams, assets, 0, currentActor, "");
    }

    function supplyCollateral(uint256 assets, uint256 seed) public asActor(seed) {
        assets = bound(assets, 1, 1e24);
        morpho.supplyCollateral(marketParams, assets, currentActor, "");
    }

    function borrow(uint256 assets, uint256 seed) public asActor(seed) {
        (, , uint128 coll) = _pos(currentActor);
        uint256 ceiling = uint256(coll).mulDivDown(oracle.price(), ORACLE_SCALE).wMulDown(marketParams.lltv) + 1;
        if (ceiling < 2) return;
        assets = bound(assets, 1, ceiling > 1e24 ? 1e24 : ceiling);
        morpho.borrow(marketParams, assets, 0, currentActor, currentActor);
    }

    function repayShares(uint256 shares, uint256 seed) public asActor(seed) {
        (, uint128 bs, ) = _pos(currentActor);
        if (bs == 0) return;
        shares = bound(shares, 1, bs);
        morpho.repay(marketParams, 0, shares, currentActor, "");
    }

    function repayAssets(uint256 assets, uint256 seed) public asActor(seed) {
        (, uint128 bs, ) = _pos(currentActor);
        if (bs == 0) return;
        (, , uint128 tba, uint128 tbs, , ) = morpho.market(id);
        uint256 debt = uint256(bs).toAssetsUp(tba, tbs);
        assets = bound(assets, 1, debt + 1); // overshoot path exercised; revert tolerated
        morpho.repay(marketParams, assets, 0, currentActor, "");
    }

    function withdraw(uint256 shares, uint256 seed) public asActor(seed) {
        (uint256 ss, , ) = _pos(currentActor);
        if (ss == 0) return;
        shares = bound(shares, 1, ss);
        morpho.withdraw(marketParams, 0, shares, currentActor, currentActor);
    }

    function withdrawCollateral(uint256 assets, uint256 seed) public asActor(seed) {
        (, , uint128 coll) = _pos(currentActor);
        if (coll == 0) return;
        assets = bound(assets, 1, coll);
        morpho.withdrawCollateral(marketParams, assets, currentActor, currentActor);
    }

    function setPrice(uint256 price) public {
        price = bound(price, ORACLE_SCALE / 10, ORACLE_SCALE * 10);
        oracle.setPrice(price);
    }

    function warp(uint256 dt) public {
        vm.warp(block.timestamp + bound(dt, 1, 365 days));
    }

    function setFee(uint256 fee) public {
        fee = bound(fee, 0, 0.15e18);
        vm.prank(owner);
        morpho.setFee(marketParams, fee);
    }

    /* LIQUIDATION HANDLERS (enforce crown claims) */

    function _isHealthy(address user) internal view returns (bool) {
        (, , uint128 tba, uint128 tbs, , ) = morpho.market(id);
        (, uint128 bs, uint128 coll) = _pos(user);
        if (bs == 0) return true;
        uint256 borrowed = uint256(bs).toAssetsUp(tba, tbs);
        uint256 maxBorrow = uint256(coll).mulDivDown(oracle.price(), ORACLE_SCALE).wMulDown(marketParams.lltv);
        return maxBorrow >= borrowed;
    }

    function _recordLiq(uint256 seized, uint256 repaidAssets, bool wasHealthy) internal {
        successfulLiquidations++;
        if (wasHealthy) healthyLiquidations++;
        if (repaidAssets < 1e6) return; // skip rounding-dominated dust
        uint256 quoted = seized.mulDivDown(oracle.price(), ORACLE_SCALE);
        uint256 ratioWad = quoted.mulDivUp(WAD, repaidAssets);
        if (ratioWad > maxLifRatioWad) maxLifRatioWad = ratioWad;
    }

    function liquidateSeized(uint256 borrowerSeed, uint256 seizedSeed, uint256 liqSeed) public {
        address borrower = actors[borrowerSeed % 4];
        (, , uint128 coll) = _pos(borrower);
        if (coll == 0) return;
        uint256 seized = bound(seizedSeed, 1, coll);
        address liquidator = actors[(borrowerSeed + liqSeed + 1) % 4];
        morpho.accrueInterest(marketParams);
        bool wasHealthy = _isHealthy(borrower);
        vm.startPrank(liquidator);
        try morpho.liquidate(marketParams, borrower, seized, 0, "") returns (uint256 s, uint256 r) {
            _recordLiq(s, r, wasHealthy);
        } catch {}
        vm.stopPrank();
    }

    function liquidateRepaid(uint256 borrowerSeed, uint256 sharesSeed, uint256 liqSeed) public {
        address borrower = actors[borrowerSeed % 4];
        (, uint128 bs, ) = _pos(borrower);
        if (bs == 0) return;
        uint256 shares = bound(sharesSeed, 1, bs);
        address liquidator = actors[(borrowerSeed + liqSeed + 2) % 4];
        morpho.accrueInterest(marketParams);
        bool wasHealthy = _isHealthy(borrower);
        vm.startPrank(liquidator);
        try morpho.liquidate(marketParams, borrower, 0, shares, "") returns (uint256 s, uint256 r) {
            _recordLiq(s, r, wasHealthy);
        } catch {}
        vm.stopPrank();
    }
}

contract NutUSDInvariantTest is Test {
    using MarketParamsLib for MarketParams;
    using MathLib for uint256;

    Morpho internal morpho;
    ERC20Mock internal loan;
    ERC20Mock internal collateralToken;
    OracleMock internal oracle;
    IrmMock internal irm;
    MarketParams internal marketParams;
    Id internal id;
    NutHandler internal handler;
    address internal feeRecipient;

    uint256 internal constant LLTV = 0.385e18;
    uint256 internal constant ORACLE_SCALE = 1e36;
    uint256 internal constant MAX_LIF = 1.15e18;
    uint256 internal constant LIF_TOL = 1e15; // 0.1% rounding tolerance, dust excluded

    function setUp() public {
        morpho = new Morpho(address(this));
        loan = new ERC20Mock();
        collateralToken = new ERC20Mock();
        oracle = new OracleMock();
        oracle.setPrice(ORACLE_SCALE);
        irm = new IrmMock();

        morpho.enableLltv(LLTV);
        morpho.enableIrm(address(irm));

        marketParams = MarketParams({
            loanToken: address(loan),
            collateralToken: address(collateralToken),
            oracle: address(oracle),
            irm: address(irm),
            lltv: LLTV
        });
        morpho.createMarket(marketParams);
        id = marketParams.id();

        feeRecipient = makeAddr("feeRecipient");
        morpho.setFeeRecipient(feeRecipient);

        handler = new NutHandler(morpho, loan, collateralToken, oracle, address(this), marketParams);

        bytes4[] memory selectors = new bytes4[](12);
        selectors[0] = handler.supply.selector;
        selectors[1] = handler.supplyCollateral.selector;
        selectors[2] = handler.borrow.selector;
        selectors[3] = handler.repayShares.selector;
        selectors[4] = handler.repayAssets.selector;
        selectors[5] = handler.withdraw.selector;
        selectors[6] = handler.withdrawCollateral.selector;
        selectors[7] = handler.liquidateSeized.selector;
        selectors[8] = handler.liquidateRepaid.selector;
        selectors[9] = handler.setPrice.selector;
        selectors[10] = handler.warp.selector;
        selectors[11] = handler.setFee.selector;

        targetSelector(FuzzSelector({addr: address(handler), selectors: selectors}));
        targetContract(address(handler));
    }

    /* INVARIANTS — nutUSD research claims */

    function invariant_aggregate_liquidity() public view {
        (uint128 tsa, , uint128 tba, , , ) = morpho.market(id);
        assertGe(tsa, tba, "aggregate liquidity broken: supply < borrow");
    }

    function invariant_supply_share_conservation() public view {
        (, uint128 tss, , , , ) = morpho.market(id);
        (uint256 feeSs, , ) = morpho.position(id, feeRecipient);
        uint256 sum = feeSs;
        for (uint256 i; i < 4; ++i) {
            (uint256 ss, , ) = morpho.position(id, handler.actors(i));
            sum += ss;
        }
        assertEq(sum, tss, "supply shares != total");
    }

    function invariant_borrow_share_conservation() public view {
        (, , , uint128 tbs, , ) = morpho.market(id);
        uint256 sum;
        for (uint256 i; i < 4; ++i) {
            (, uint128 bs, ) = morpho.position(id, handler.actors(i));
            sum += bs;
        }
        assertEq(sum, tbs, "borrow shares != total");
    }

    function invariant_idle_balance() public view {
        (uint128 tsa, , uint128 tba, , , ) = morpho.market(id);
        assertGe(
            loan.balanceOf(address(morpho)) + tba,
            tsa,
            "morpho holds less idle than ledger requires"
        );
    }

    function invariant_collateral_ledger() public view {
        uint256 sum;
        for (uint256 i; i < 4; ++i) {
            (, , uint128 coll) = morpho.position(id, handler.actors(i));
            sum += coll;
        }
        assertEq(collateralToken.balanceOf(address(morpho)), sum, "collateral ledger mismatch");
    }

    function invariant_healthy_never_liquidated() public view {
        assertEq(handler.healthyLiquidations(), 0, "HEALTHY POSITION LIQUIDATED");
    }

    function invariant_lif_cap_385() public view {
        assertLe(handler.maxLifRatioWad(), MAX_LIF + LIF_TOL, "LIF cap exceeded at 38.5%");
    }
}

/// Deterministic proofs of the two crown claims (non-fuzz anchors).
contract NutUSDStaticTest is Test {
    using MarketParamsLib for MarketParams;
    using MathLib for uint256;

    uint256 internal constant ORACLE_SCALE = 1e36;
    uint256 internal constant LLTV = 0.385e18;

    Morpho internal morpho;
    ERC20Mock internal loan;
    ERC20Mock internal collat;
    OracleMock internal oracle;
    IrmMock internal irm;
    MarketParams internal mp;
    Id internal id;
    address internal supplier = makeAddr("supplier");
    address internal borrower = makeAddr("borrower");
    address internal liquidator = makeAddr("liquidator");

    function setUp() public {
        morpho = new Morpho(address(this));
        loan = new ERC20Mock();
        collat = new ERC20Mock();
        oracle = new OracleMock();
        oracle.setPrice(ORACLE_SCALE);
        irm = new IrmMock();

        morpho.enableLltv(LLTV);
        morpho.enableIrm(address(irm));

        mp = MarketParams({
            loanToken: address(loan),
            collateralToken: address(collat),
            oracle: address(oracle),
            irm: address(irm),
            lltv: LLTV
        });
        morpho.createMarket(mp);
        id = mp.id();
        loan.setBalance(supplier, 1e24);
        loan.setBalance(liquidator, 1e24);
        collat.setBalance(borrower, 1e24);
        vm.startPrank(supplier);
        loan.approve(address(morpho), type(uint256).max);
        morpho.supply(mp, 1e21, 0, supplier, "");
        vm.stopPrank();
        vm.startPrank(borrower);
        collat.approve(address(morpho), type(uint256).max);
        morpho.supplyCollateral(mp, 2e18, borrower, "");
        vm.stopPrank();
        vm.prank(liquidator);
        loan.approve(address(morpho), type(uint256).max);
    }

    function test_healthy_position_not_liquidatable() public {
        vm.prank(borrower);
        morpho.borrow(mp, 0.5e18, 0, borrower, borrower); // 25% LTV, healthy

        vm.prank(liquidator);
        vm.expectRevert("position is healthy");
        morpho.liquidate(mp, borrower, 0.1e18, 0, "");
    }

    function test_lif_cap_full_close() public {
        vm.prank(borrower);
        morpho.borrow(mp, 0.5e18, 0, borrower, borrower); // 25% LTV
        oracle.setPrice(0.5e36); // 2x crash -> maxBorrow 0.385e18 < debt 0.5e18 -> unhealthy

        (, uint128 bs, ) = morpho.position(id, borrower);
        vm.prank(liquidator);
        (uint256 seized, uint256 repaidAssets) = morpho.liquidate(mp, borrower, 0, bs, "");

        uint256 quoted = seized.mulDivDown(oracle.price(), ORACLE_SCALE);
        uint256 ratioWad = quoted.mulDivUp(1e18, repaidAssets);
        assertLe(ratioWad, 1.15e18 + 2, "LIF cap exceeded");
        (, uint128 bsAfter, uint128 collAfter) = morpho.position(id, borrower);
        assertEq(collAfter, 2e18 - seized, "collateral mismatch");
        assertEq(bsAfter, 0, "debt not closed");
    }
}
