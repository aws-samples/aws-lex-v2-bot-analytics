# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2021-09-10
### Added
- Custom Widget to display top N slots and session attribute values
### Changed
- Bot tester now sets session attributes and sends audio utterances

## [0.2.0] - 2021-09-03
### Fixed
- Changed metric namespace to include bot locale
- Added bot and locale ID filters to CloudWatch Insight rules/queries
- Fixed handling of ReadyForFullfilment state and empty data in conversation
  path widget
### Removed
- Removed session count value from Activity section due to exceptions if the
  selected time range is larger than 24 hours

## [0.1.0] - 2021-08-26
### Added
- Initial release

[Unreleased]: https://github.com/aws-samples/aws-lex-v2-bot-analytics/compare/v0.3.0...develop
[0.3.0]: https://github.com/aws-samples/aws-lex-v2-bot-analytics/releases/tag/v0.3.0
[0.2.0]: https://github.com/aws-samples/aws-lex-v2-bot-analytics/releases/tag/v0.2.0
[0.1.0]: https://github.com/aws-samples/aws-lex-v2-bot-analytics/releases/tag/v0.1.0