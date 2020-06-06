# flog

Generates a static website from an org-mode file. Tags and properties become filters. Dependencies: markdown, jinja2.


```
python3 flog.py orgfile.org 
```

Everything in flog/resources/ will be copied, along with the generated HTML, to html/ in the current directory. Try demo.org as an example.