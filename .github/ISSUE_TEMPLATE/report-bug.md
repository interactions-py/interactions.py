---
name: Report Bug
about: Create an Issue to report a bug with/about the library.
title: "[BUG] "
labels: bug
assignees: goverfl0w

---

**Describe the bug**
Please give us an in-depth description of the bug you're having.

**Reproducing steps**
These are the steps I took in order to produce this bug, which should be able to be reproduced for everyone else as well.

1. Import the module in Python.
2. Create a client variable for the library.
3. Try creating a slash command.
4. See the traceback error given in the terminal or logger file.

**What's normally expected**
When I create a slash command, the command should be created and functional.

**What actually happened**
Instead, I received this traceback error given from my Python terminal:

```
Traceback (most recent call last):
  File "A:\Amogus\Python\interactions-bot\main.py", line 6
    raise SussyBaka("your code doesn't work, silly!")
          ^

SussyBaka: your code doesn't work, silly!
```

**Versions**
- [ ] I am using discord.py versions 1.7 and below with my code.
    - [ ] I am using 2.0 or higher, or a modified fork.
- [ ] I am using dis-snek with my code.
- [ ] I am not using any of the listed above and am using the library code alone.
