// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title Controllable Chainlink-style aggregator for the XI oracle failure matrix.
/// @dev Matches the exact call surface MorphoChainlinkOracleV2 uses via
///      ChainlinkDataFeedLib: latestRoundData() and decimals(). Mode flags:
///      0 = serve, 1 = latestRoundData reverts (broken feed).
contract MockAggregator {
    uint80  public roundId;
    int256  public answer;
    uint256 public startedAt;
    uint256 public updatedAt;
    uint80  public answeredInRound;
    uint8   public aggDecimals;
    string  public aggDescription;
    uint8   public mode;

    constructor(int256 ans, uint8 dec, string memory desc) {
        answer = ans;
        aggDecimals = dec;
        aggDescription = desc;
        roundId = 1;
        answeredInRound = 1;
        startedAt = block.timestamp;
        updatedAt = block.timestamp;
    }

    function setAnswer(int256 a) external {
        answer = a;
        roundId += 1;
        answeredInRound = roundId;
        startedAt = block.timestamp;
        updatedAt = block.timestamp;
    }

    function setUpdatedAt(uint256 t) external { updatedAt = t; }

    function setMode(uint8 m) external { mode = m; }

    function decimals() external view returns (uint8) { return aggDecimals; }

    function description() external view returns (string memory) { return aggDescription; }

    function version() external pure returns (uint256) { return 1; }

    function latestRoundData()
        external
        view
        returns (uint80, int256, uint256, uint256, uint80)
    {
        require(mode == 0, "mock: broken feed");
        return (roundId, answer, startedAt, updatedAt, answeredInRound);
    }

    function getRoundData(uint80)
        external
        view
        returns (uint80, int256, uint256, uint256, uint80)
    {
        require(mode == 0, "mock: broken feed");
        return (roundId, answer, startedAt, updatedAt, answeredInRound);
    }
}
