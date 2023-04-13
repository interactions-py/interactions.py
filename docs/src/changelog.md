# Changelog

Here you can find the changelog for the library. This is a list of all the changes that have been made to the library, since V5.0.0. 
In breaking changes, the breaking change is signified by a `💥`


## 5.0.1 - April 12th, 2023
- Fix: copy checks when inheriting
      - When inheriting checks, slash commands would pass in their own checks to the subcommand. This makes sense logically, however, what wasn't being caught was that these were being passed by reference, and so any edit to the checks in one subcommand would affect potentially EVERY command.
- Build: Ensure opus `dll`s are included in pypi releases