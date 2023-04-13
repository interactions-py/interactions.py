# Changelog

Here you can find the changelog for the library. This is a list of all the changes that have been made to the library, since V5.0.0. 
In breaking changes, the breaking change is signified by a `💥`

## 5.1.0 - TBA
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
