# Changelog

Here you can find the changelog for the library. This is a list of all the changes that have been made to the library, since V5.0.0.
In breaking changes, the breaking change is signified by a `💥`


## **Release 5.6.0 - June 2nd, 2023**
### What's New
- docs: Document `send_command_tracebacks` in the Error Tracking guide  in https://github.com/interactions-py/interactions.py/pull/1422
- feat: add missing args to Guild.create_forum_post  in https://github.com/interactions-py/interactions.py/pull/1417
- docs: fix errors in the bot example and add intent  in https://github.com/interactions-py/interactions.py/pull/1416
- feat: Provide Guild ID in GuildLeft event  in https://github.com/interactions-py/interactions.py/pull/1435
- feat: add support for sentry argument  in https://github.com/interactions-py/interactions.py/pull/1433

### What's Fixed
- fix: correctly work with Permissions.NONE when passed into Guild.create_role  in https://github.com/interactions-py/interactions.py/pull/1421
- fix: don't assume msg reference always has msg id  in https://github.com/interactions-py/interactions.py/pull/1423
- fix: prevent udp ka from throwing error on close  in https://github.com/interactions-py/interactions.py/pull/1425
- fix emoji.edit allowing roleslist  in https://github.com/interactions-py/interactions.py/pull/1427
- fix: Don't apply guild_id to messages fetched from DM history  in https://github.com/interactions-py/interactions.py/pull/1424
- fix: prevent udp ka from throwing error on close  in https://github.com/interactions-py/interactions.py/pull/1425
- fix: prevent already-responded error when using discord image proxy workaround  in https://github.com/interactions-py/interactions.py/commit/859323ac11ed63c3e13a2a666421b0e71d0d25d1

**Full Changelog:** https://github.com/interactions-py/interactions.py/compare/5.5.1...5.6.0


## **Release 5.5.1 - May 23th, 2023**
### What's Fixed
- fix: Compatibility with discord_typings 0.6.0  in https://github.com/interactions-py/interactions.py/pull/1418

**Full Changelog:** https://github.com/interactions-py/interactions.py/compare/5.5.0...5.5.1


## **Release 5.5.0 - May 21th, 2023**
### What's New
- feat: Handle async checks in wait_for_component  in https://github.com/interactions-py/interactions.py/pull/1406
- feat: bypass discord's broken image proxy  in https://github.com/interactions-py/interactions.py/pull/1414

**Full Changelog:** https://github.com/interactions-py/interactions.py/compare/5.4.0...5.5.0


## **Release 5.4.0 - May 17th, 2023**
### What's New
- feat: add regex support for modal callback  in https://github.com/interactions-py/interactions.py/pull/1388
- feat: sort roles  in https://github.com/interactions-py/interactions.py/pull/1397
- feat: allow .purge to return messages  in https://github.com/interactions-py/interactions.py/pull/1396
- feat: support http proxies  in https://github.com/interactions-py/interactions.py/pull/1398
- feat: send not ready messages if requested  in https://github.com/interactions-py/interactions.py/pull/1389
- feat: support recovery from additional WebSocket close codes  in https://github.com/interactions-py/interactions.py/pull/1403

### What's Fixed
- fix: properly pass guild_id to http's get_guild  in https://github.com/interactions-py/interactions.py/pull/1394
- fix:  Pin our minimum version of attrs to >=22.1  in https://github.com/interactions-py/interactions.py/pull/1392
- fix: correctly handle message references  in https://github.com/interactions-py/interactions.py/pull/1395

**Full Changelog:** https://github.com/interactions-py/interactions.py/compare/5.3.1...5.4.0


## **Release 5.3.1 - May 6th, 2023**
- fix: use wrap partial on commands  in https://github.com/interactions-py/interactions.py/pull/1391

**Full Changelog:** https://github.com/interactions-py/interactions.py/compare/5.3.0...5.3.1


## **Release 5.3.0 - May 6th, 2023**
### What's New
- feat: add BaseEvent.client alias property  in https://github.com/interactions-py/interactions.py/pull/1368
- feat: add `component` property to `ComponentContex`  in https://github.com/interactions-py/interactions.py/pull/1371
- feat: add support for mentioning onboarding  in https://github.com/interactions-py/interactions.py/pull/1373
- feat: implement new automod features  in https://github.com/interactions-py/interactions.py/pull/1372
- feat: add missing perms  in https://github.com/interactions-py/interactions.py/pull/1374
- feat: support audit log 180  in https://github.com/interactions-py/interactions.py/pull/1379
- feat: support clyde channel flag  in https://github.com/interactions-py/interactions.py/pull/1375
- feat: add support for voice messages  in https://github.com/interactions-py/interactions.py/pull/1376
- feat: pass event object based on listeners signature  in https://github.com/interactions-py/interactions.py/pull/1367
- feat: `SlashCommandChoice` as parameter for `AutoCompleteContext.send`  in https://github.com/interactions-py/interactions.py/pull/1380

### What's Fixed
- fix: account for discord's discrim change  in https://github.com/interactions-py/interactions.py/pull/1384
- fix: copy prefixed cmd set when unloading ext  in https://github.com/interactions-py/interactions.py/pull/1385
- fix: pass a Member as author of MessageReactionRemove  in https://github.com/interactions-py/interactions.py/pull/1370
- fix: pass default_member_permissions in SlashCommand.group()  in https://github.com/interactions-py/interactions.py/pull/1369

**Full Changelog:** https://github.com/interactions-py/interactions.py/compare/5.2.0...5.3.0


## **Release 5.2.0 - April 30th, 2023**
### What's New
- feat: add `rate_limit_per_user` param for create thread methods  in https://github.com/interactions-py/interactions.py/pull/1359
- feat: format ratelimit messages with major params  in https://github.com/interactions-py/interactions.py/pull/1360
- feat: add `user` & `member` props to auto mod action  in https://github.com/interactions-py/interactions.py/pull/1358
- Added poll option to jurriged ext by @Proxy in https://github.com/interactions-py/interactions.py/pull/1364

### What's Fixed
- fix:  Resolve failing linter checks  in https://github.com/interactions-py/interactions.py/pull/1361
- fix migration oversights in debug ext
- fix: handle a user not passing a cooldown system to the cooldown decorator

**Full Changelog:** https://github.com/interactions-py/interactions.py/compare/5.1.0...5.2.0


## **Release 5.1.0 - April 21st, 2023**
### What's New
- feat: support regex component callbacks  in https://github.com/interactions-py/interactions.py/pull/1332
- chore: switch to MIT license  in https://github.com/interactions-py/interactions.py/pull/1334
- feat: add audit new mod events to audit log enum  in https://github.com/interactions-py/interactions.py/pull/1335
- refactor: change log level of missing value to warning  in https://github.com/interactions-py/interactions.py/pull/1339
- feat: add missing message types  in https://github.com/interactions-py/interactions.py/pull/1338
- feat: support avatar decorations  in https://github.com/interactions-py/interactions.py/pull/1329
- feat: sync improvements  in https://github.com/interactions-py/interactions.py/pull/1328
- feat: rate limit improvements  in https://github.com/interactions-py/interactions.py/pull/1321
- refactor: Update readme shields and add recent extensions  in https://github.com/interactions-py/interactions.py/pull/1348
- feat: caching improvements  in https://github.com/interactions-py/interactions.py/pull/1350
- feat: add reset_with_key and get_cooldown_time_with_key  in https://github.com/interactions-py/interactions.py/pull/1345
- docs: adjust and fix many parts of the docs  in https://github.com/interactions-py/interactions.py/pull/1353

### What's Fixed
- fix: wrong check condition in the component callback  in https://github.com/interactions-py/interactions.py/pull/1352
- chore: Update filesize to new 25mb discord limit  in https://github.com/interactions-py/interactions.py/pull/1346

**Full Changelog:** https://github.com/interactions-py/interactions.py/compare/5.0.1...5.1.0


## **Release 5.0.1 - HOTFIX - April 12th, 2023**
- fix: copy checks when inheriting
  	- When inheriting checks, slash commands would pass in their own checks to the subcommand. This makes sense logically, however, what wasn't being caught was that these were being passed by reference, and so any edit to the checks in one subcommand would affect potentially EVERY command.
- build: Ensure opus `dll`s are included in pypi releases


## **Release 5.0.0 - April 10th, 2023**
- Python3.10 is now the minimum supported python version
- The cache takes centre stage - accessing client.http should not be required
- The client is now substantially more error tolerant. Your commands can fail spectacularly, and the client wont drop an event
- Full API coverage (excluding some pre-release bits)
- Voice Playback and recording built-in
vMany of the old exts are now merged in (check out [here](https://github.com/interactions-py/interactions.py/tree/5.0.0/interactions/ext))
- Performance is improved
- UX has subjectively improved - this is because this release was based heavily on feedback from users

Docs: https://interactions-py.github.io/interactions.py/<br/>
For NAFF users: [NAFF Migration Guide](https://interactions-py.github.io/interactions.py/Guides/99%202.x%20Migration_NAFF/)<br/>
For i.py v4: [I.PY V4 Migration Guide](https://interactions-py.github.io/interactions.py/Guides/98%20Migration%20from%204.X/)<br/>

Full Changelog https://github.com/interactions-py/interactions.py/compare/4.4.0...5.0.0
