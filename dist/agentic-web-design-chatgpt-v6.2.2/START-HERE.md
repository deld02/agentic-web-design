# ChatGPT runtime — v6.2.2

This is the current execution package, not the historical repository. The only roles are `00` through `07`; the only pipeline authority is `config/pipeline.json`.

For a real project, first save the user brief and run:

```text
python tools/evaluation_harness.py chat-start --brief-file <brief>
```

Then complete only the returned stage and use `chat-next`. During `creative-master`, generate a real raster and register it with `chat-image` before advancing.

Do not search for or reconstruct earlier architectures. This pack intentionally contains no historical audits, changelog or superseded decision log.
