# Pagination

> Pagination, also known as paging, is the process of dividing a document into discrete pages, either electronic pages or printed pages.

We've all hit that point where Discord won't let you send enough characters, at that point you can either flood the channel with multiple messages, or you can start paginating your messages.

NAFF comes builtin with a pagination utility that splits your messages up into pages, which your user can navigate through.

![Paginator example](../images/paginator%20example.png)

To use it, you only need 3 lines.

```python
from naff.ext.paginators import Paginator

paginator = Paginator.create_from_string(bot, your_content, page_size=1000)
await paginator.send(ctx)
```

But let's say you have fancy embedded content you want to use. Well don't worry, NAFF can handle that too:
```python
embeds = [Embed("Page 1 content"), Embed("Page 2 embed"), Embed("Page 3 embed"), Embed("Page 4 embed")]
paginator = Paginator.create_from_embeds(bot, *embeds)
```

Paginators are configurable, you can choose which buttons show, add timeouts, add select menu navigation, and even add callbacks. To see your options, check out their documentation [here](/API Reference/ext/paginators).
