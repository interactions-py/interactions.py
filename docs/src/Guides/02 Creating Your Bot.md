# Creating Your Bot

To make a bot on Discord, you must first create an application on Discord. Thankfully, Discord has made this process very simple:

1. Login to the [:fontawesome-brands-discord:Discord website](https://discord.com/)

2. Navigate to the [Developer Application page](https://discord.com/developers/applications)

3. Press `New Application`
   <br>![New Application Button](../images/CreatingYourBot/NewApplication.png "The New Application Button")

4. Give your application a name, and press `Create`
    <br>![Create Application Dialogue](../images/CreatingYourBot/CreateAnApplication.png "The Create Application Dialogue")

    ??? note
        Don't worry if there isn't a `team` option, this only appears if you have a developer team.
        If you have a team and want to assign your bot to it, use this.

5. In the `Bot` tab, press `Add bot`
    <br>![img.png](../images/CreatingYourBot/BuildABot.png "The Add bot button and text")

6. You now have a bot! You're going to want to press `Reset Token` to get your bot's token, so you can start coding
    <br>![A section that shows your bot and its token](../images/CreatingYourBot/BotUserToken.png "The bot display")

    ??? note
        You may (or may not) be asked to enter your password or 2FA authentication code to confirm this action.

    !!! warning "Warning: Do not share your token!"
        Think of this token as your bots username **and** password in one. You should **never** share this with someone else.
        If someone has your token, they can do absolutely anything with your bot, from banning every member in every server to
        leaving every server your bot is in.

        If you think you have leaked your token, press `Reset Token` on the same page you copy your token on,
        this will revoke your token (logging out all exisitng sessions), and generate a new token for you.

        :fontawesome-brands-github:Github will automatically revoke your token if you accidentally commit it, but don't rely on this
        as a crutch, keep your token safe.


## Inviting your bot!

So you've created a bot, but it's not in a server yet. Lets fix that.

1. On the [Developer Application page](https://discord.com/developers/applications) from above, select your bot

2. Navigate to the `OAuth2` tab

3. Scroll down to the `URL Generator`. This is where we're going to create our invite link
    <br>![A widget that creates your invite link](../images/CreatingYourBot/oauth2Gen.png "The invite oauth2 generator")

4. Select the `bot` option, and if you want to use application commands, select `applications.commands` as well

5. If your bot needs any special permissions, select those below
    <br>![A widget that lets you pick what your bot's permissions are](../images/CreatingYourBot/botPerms.png "Bot Permissions")

6. Now you have an invite link! Simply use this to invite your bot.

    !!! note
        You need `manage server` permissions to add a bot to a server
