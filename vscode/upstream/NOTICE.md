# Notice

The four JSON files in this directory are unmodified copies of the Dark+ and Light+ theme definitions from [microsoft/vscode](https://github.com/microsoft/vscode/tree/main/extensions/theme-defaults/themes) (`dark_vs.json`, `dark_plus.json`, `light_vs.json` and `light_plus.json`).

The Afterglow VS Code themes use them as a structural reference: the generator keeps every TextMate scope rule and semantic token override that Dark+ and Light+ define, and replaces each colour with the matching Afterglow palette colour. Without these files the generator would not know which scopes Dark+ and Light+ colour.

```text
MIT License

Copyright (c) 2015 - present Microsoft Corporation

All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
