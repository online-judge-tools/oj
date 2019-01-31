# Login with cookies

If you don't want to give my password to this program, you can use this giving only your session tokens. 

Here, we explain about logging in yukicoder (Japanese online judge service).
In yukicoder, You can login with password or github account or twitter account.

1. Login yukicoder with the browser.

Please access https://yukicoder.me/ and log in with the browser.

2. Get cookies from the browser.

I used chrome with ["EditThisCookie" Plugin](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?), but you can choose other plugin or other browser.

Please copy REVEL_SESSION value.

![GetCookie](https://user-images.githubusercontent.com/8858287/52058622-31674e80-25ab-11e9-840d-f3960aee8711.png)

3. Generate dummy session cookie.

```
$ oj login -u dummy -p dummy https://yukicoder.me/

[x] service recognized: <onlinejudge.service.yukicoder.YukicoderService object at 0x7fb468d332b0>: https://yukicoder.me/
[x] load cookie from: /home/ryo/.local/share/online-judge-tools/cookie.jar
[x] GET: https://yukicoder.me/auth/github
[x] 200 OK
[x] POST: https://github.com/session
[x] 200 OK
[-] You failed to sign in. Wrong user ID or password.
[x] save cookie to: /home/ryo/.local/share/online-judge-tools/cookie.jar
```

Since where cookie.jar is saved depends on the environment, you have to confirm that by console message.
In this case, cookie.jar is saved to `/home/ryo/.local/share/online-judge-tools/cookie.jar`.

4. Edit cookie.jar.

Open cookie.jar with your text editer, you can find session cookie for yukicoder.

```
Set-Cookie3: REVEL_SESSION="XXXXX"; path="/"; domain="yukicoder.me"; path_spec; expires="2019-02-28 14:53:09Z"; HttpOnly=None; version=0
```

Please replace current `REVEL_SESSION` value to value which you copied by the browser.

5. Confirm logged in.

```
$ oj login https://yukicoder.me/

[x] service recognized: <onlinejudge.service.yukicoder.YukicoderService object at 0x7f4467a0a2b0>: https://yukicoder.me/
[x] load cookie from: /home/ryo/.local/share/online-judge-tools/cookie.jar
[x] GET: https://yukicoder.me/auth/github
[x] 200 OK
[*] You have already signed in.
[x] save cookie to: /home/ryo/.local/share/online-judge-tools/cookie.jar
```

You can find the sentence `You have already signed in.`.
Now, you can download testcases from yukicoder.

