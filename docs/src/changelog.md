# Changelog

Here you can find the changelog for the library. This is a list of all the changes that have been made to the library, since V5.0.0.
In breaking changes, the breaking change is signified by a `💥`

## 5.4.0 - May 17th, 2023
- Feat: Add regex support for modal callback
- Feat: Sort roles
- Feat: Allow .purge to return messages
- Feat: Support http proxies
- Feat: Send not ready messages if requested
- Feat: Support recovery from additional WebSocket close codes
- Fix: Properly pass guild_id to http's get_guild
- Fix: Pin our minimum version of attrs to >=22.1
- Fix: Correctly handle message references

## 5.3.1 - May 6th, 2023
- Fix: Use wrap partial on commands

## 5.3.0 - May 6th, 2023
- Feat: Add BaseEvent.client alias property
- Feat: Add `component` property to `ComponentContext`
- Feat: Add support for mentioning onboarding
- Feat: Implement new automod features
- Feat: Add missing perms
- Feat: Support audit log
- Feat: Support clyde channel flag
- Feat: Add support for voice messages
- Feat: Pass event object based on listeners signature
- Feat: `SlashCommandChoice` as parameter for `AutoCompleteContext.send`
- Fix: Add missing MessageFlag
- Fix: Account for discord's discrim change
- Fix: Copy prefixed cmd set when unloading ext
- Fix: Pass a Member as author of MessageReactionRemove
- Fix: Pass default_member_permissions in SlashCommand.group()

## 5.2.0 - April 30th, 2023
- Feat: Added `ratelimit` parameter to create thread methods
- Feat: Format ratelimit messages with major params
- Feat: Added user & member props to auto mod action
- Feat: Added poll option to jurriged ext
- Fix: Resolve failing linter checks
- Fix: Migration oversights in debug ext
- Fix: Handle a user not passing a cooldown system to the cooldown decorator

## 5.1.0 - April 21st, 2023
- Feat: Add support for regex component callbacks
- Feat: Add new audit log events to enums
- Refactor: Change log level of missing enum value from error to warning
- Feat: Add missing message types to enums
- Feat: Add support for Avatar Decorations
- Chore: Switch library license to MIT
- Build: Add pypi alias `interactions.py`
- Feat: Enhance cooldown system
  	- Adds new cooldown strategies and allows fetching of the cooldown object using an ID instead of context object

## 5.0.1 - April 12th, 2023
- Fix: copy checks when inheriting
  	- When inheriting checks, slash commands would pass in their own checks to the subcommand. This makes sense logically, however, what wasn't being caught was that these were being passed by reference, and so any edit to the checks in one subcommand would affect potentially EVERY command.
- Build: Ensure opus `dll`s are included in pypi releases
