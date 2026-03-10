# SOURCE OF TRUTH

- Никогда не считать runtime/generated файл источником истины, если есть master-конфиг, patcher, generator или sync pipeline.
- Перед любой правкой определить:
  - master source;
  - generated/runtime files;
  - что нельзя править напрямую;
  - что перезаписывается при рестарте, bootstrap, sync или patch.
