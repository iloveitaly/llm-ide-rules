# Changelog

## [0.7.0](https://github.com/iloveitaly/llm-ide-rules/compare/v0.6.0...v0.7.0) (2026-01-27)


### Features

* **download:** support include_patterns for instruction files ([a899d00](https://github.com/iloveitaly/llm-ide-rules/commit/a899d00cf1ab919228209eaf9637325cf69e52b0))
* generate agent-specific root docs and parse markdown sections ([963b9e4](https://github.com/iloveitaly/llm-ide-rules/commit/963b9e4aa3e3082f5d663f6bd60d7f9b9ecadcff))


### Bug Fixes

* **markdown_parser:** handle glob directive case and spacing ([29af02a](https://github.com/iloveitaly/llm-ide-rules/commit/29af02a05725ca13b08d997207f89275be2234f0))


### Documentation

* add globs info for language and test sections ([5867c83](https://github.com/iloveitaly/llm-ide-rules/commit/5867c83de13c271adacce449c18bdddf35f06db0))
* move db/orm instructions from python to python-app docs ([9284040](https://github.com/iloveitaly/llm-ide-rules/commit/928404077e04c37bfd4f644ae9655b106b31c6a0))
* reorganize and clarify python app directory guidance ([d85611c](https://github.com/iloveitaly/llm-ide-rules/commit/d85611c3f9f8f605a85837ab53160a350ea11db1))

## [0.6.0](https://github.com/iloveitaly/llm-ide-rules/compare/v0.5.0...v0.6.0) (2026-01-26)


### Features

* add commands.md ([aabd520](https://github.com/iloveitaly/llm-ide-rules/commit/aabd520abef1aa2373812932f8189b38125172e6))
* **agents:** add Claude, Gemini, and GitHub agent implementations ([a861552](https://github.com/iloveitaly/llm-ide-rules/commit/a861552550a2e153b0cbfc1a0d6c5abe5d08e2c6))
* **cli:** add global verbose option and improve user feedback ([ae6d5de](https://github.com/iloveitaly/llm-ide-rules/commit/ae6d5de49fa3de0daeffe4ff7764dd770e2d37b6))
* **explode:** support single agent with --agent option ([3351ac3](https://github.com/iloveitaly/llm-ide-rules/commit/3351ac3e8fa6075049a1386c86063e9ce6e166e8))
* set default log level and configure verbose in CLI init ([c8a012a](https://github.com/iloveitaly/llm-ide-rules/commit/c8a012a0f5fa7ea3473fdb62216ccb65dc3adb2a))
* support opencode command format and tomli-w for toml output ([e79a144](https://github.com/iloveitaly/llm-ide-rules/commit/e79a144a1d408b2fffd04d57a6f49cf606a7fb01))


### Bug Fixes

* correct structlog-config version in dependencies list ([23780ce](https://github.com/iloveitaly/llm-ide-rules/commit/23780ce963205fbc3d8461331eb8b3ae808c8671))
* handle manual-only sections in rule file generation ([8ad0143](https://github.com/iloveitaly/llm-ide-rules/commit/8ad014382c6493ec454a408dd05976ff4bdaca19))


### Documentation

* add commands.md with detailed dev and project instructions ([7eff67d](https://github.com/iloveitaly/llm-ide-rules/commit/7eff67db206fd8c2c33dce77c0c874979b4b5cdd))
* add IDE format comparison table to README.md ([f6d5afa](https://github.com/iloveitaly/llm-ide-rules/commit/f6d5afa022c22301a6216d1264b60d0b65d67c46))
* clarify dev instructions and pnpm usage in docs ([e4b8bc9](https://github.com/iloveitaly/llm-ide-rules/commit/e4b8bc94aa308ea540e1c1392217a9e6864acaa7))
* clarify pnpm usage and reorganize dev instructions ([417dc2a](https://github.com/iloveitaly/llm-ide-rules/commit/417dc2a6580fa00271bbb5e002b4a8fee02374b3))
* clarify python package management and update applyTo glob pattern ([5fe5fb1](https://github.com/iloveitaly/llm-ide-rules/commit/5fe5fb17b21d86c84baafa27219a8b5165aa8c0c))
* document OpenCode format and update CLI usage examples ([353c103](https://github.com/iloveitaly/llm-ide-rules/commit/353c1033448c9352f58c33a71a9e32eb90c721ec))
* expand python app module layout and folder purposes ([06671c1](https://github.com/iloveitaly/llm-ide-rules/commit/06671c122ffe6f44957d7a550660f3117cda2fd7))
* expand python app structure guidelines and module roles ([9784d9f](https://github.com/iloveitaly/llm-ide-rules/commit/9784d9f4d6da05f414f531ae5d79955fb4371a0a))
* fix prompt syntax and update section titles for consistency ([7ed21e6](https://github.com/iloveitaly/llm-ide-rules/commit/7ed21e6038919bbd8378c38c5c97690135ee10e0))
* **opencode:** add new command markdowns for workflow rules ([f30578d](https://github.com/iloveitaly/llm-ide-rules/commit/f30578dea8de50f0490b1580685ef28a44421391))
* recommend section comments in integration browser tests ([40e883b](https://github.com/iloveitaly/llm-ide-rules/commit/40e883b1b8290f57c6b0d0aafccefa97eb9e06b7))
* remove duplicate git clone instructions from README ([b639e5e](https://github.com/iloveitaly/llm-ide-rules/commit/b639e5ea1fa4d7729b39d247cb15ad415d18477a))
* remove environment variable and secrets management section ([ff27f2a](https://github.com/iloveitaly/llm-ide-rules/commit/ff27f2a126363709af5a7f538c2ec5da82591a41))
* remove outdated testing and implementation instructions ([2846cb2](https://github.com/iloveitaly/llm-ide-rules/commit/2846cb2a6f0673e057fc29be7ef51042a1ba9cad))
* remove python script and typescript docstring guidelines ([abc17e5](https://github.com/iloveitaly/llm-ide-rules/commit/abc17e52d3e9678ca9ab31a5a7a8d438985d54f6))
* reorder sections and move TypeScript docstring guidance ([8dbbfe3](https://github.com/iloveitaly/llm-ide-rules/commit/8dbbfe341dc74eb3733a895cce8e4875bd099e20))
* reorganize secrets and backend notes, clarify app structure ([c9dc712](https://github.com/iloveitaly/llm-ide-rules/commit/c9dc7120562378544651b31fc540a5b9bce7f388))
* **rules:** update package management and apply headers in mdc files ([0f8e8ff](https://github.com/iloveitaly/llm-ide-rules/commit/0f8e8ffb004c6bf60d0721978ff76443f50ee93c))
* simplify readme, improve install and usage details ([d4c9a5d](https://github.com/iloveitaly/llm-ide-rules/commit/d4c9a5d3eea0216b625a5eeb89bae7b1c722faca))
* update dev instructions and remove redundant package commands ([3f9614c](https://github.com/iloveitaly/llm-ide-rules/commit/3f9614c3dbaf2f85d92b4b33799e844d0f89af76))
* update dev instructions to clarify rule usage and file name ([4940408](https://github.com/iloveitaly/llm-ide-rules/commit/494040875881b3c911f818a0ecb62c7a5f70f224))
* update pnpm usage instructions in instructions.md ([5ebc27a](https://github.com/iloveitaly/llm-ide-rules/commit/5ebc27ab176fbe2e1ed4e304907f52432d36699b))
* update python section globs and package install guidance ([afcd4cb](https://github.com/iloveitaly/llm-ide-rules/commit/afcd4cbe2d1e5aab59ad49a8e520cdc1c26d0e1b))

## [0.5.0](https://github.com/iloveitaly/llm-ide-rules/compare/v0.4.0...v0.5.0) (2025-11-27)


### Features

* add claude and gemini command generation, update unmapped section handling ([2eebc36](https://github.com/iloveitaly/llm-ide-rules/commit/2eebc3665b8e4c0c95223d11c1c25b7ef825fabc))


### Documentation

* clarify pnpm usage instructions and add reference to [@local](https://github.com/local).md ([6000c0b](https://github.com/iloveitaly/llm-ide-rules/commit/6000c0bf585a8fd4d282e8ec4e4ac06e7a0eef3a))

## [0.4.0](https://github.com/iloveitaly/llm-ide-rules/compare/v0.3.0...v0.4.0) (2025-11-06)


### Features

* add delete command to remove downloaded instruction files ([cdb6b7f](https://github.com/iloveitaly/llm-ide-rules/commit/cdb6b7f7c7ba70f15f639e2164fa2b21a3016cd3))


### Documentation

* add browser usage instructions for dev server ([9de24a3](https://github.com/iloveitaly/llm-ide-rules/commit/9de24a3f77d6eb6da070a7e724070decc90609a6))
* add standalone Python script guidelines for Cursor ([1f14442](https://github.com/iloveitaly/llm-ide-rules/commit/1f14442c04c5dfe688ad8d6ee8faef34c8c98dfa))
* clarify instructions and expand testing/debugging guidance ([12311d7](https://github.com/iloveitaly/llm-ide-rules/commit/12311d7ccfc8438538569a46e4e67a98ac646e4d))
* clarify linting, pnpm usage, and test troubleshooting ([26ed01f](https://github.com/iloveitaly/llm-ide-rules/commit/26ed01fba191702a8e973d72ab5829227594a1e2))
* clarify supported AI assistant command formats in README ([a384e3d](https://github.com/iloveitaly/llm-ide-rules/commit/a384e3d87179064d0faaf965e3c91e5cb331eb54))
* clarify system package installation and comments policy in instructions ([3e9a9d7](https://github.com/iloveitaly/llm-ide-rules/commit/3e9a9d7f00ab93ea982e3fc42ee5b100697176ec))
* clarify test and coding instructions, add dev-in-browser prompt ([852b64c](https://github.com/iloveitaly/llm-ide-rules/commit/852b64c44869c8a0a56a5fdc6289a0c37be79d19))
* **commands:** add instructions for writing concise README.md ([ba4823a](https://github.com/iloveitaly/llm-ide-rules/commit/ba4823a37eaf46fdc8173832ebf53242df939f4a))
* document delete command and add command format comparison ([200742d](https://github.com/iloveitaly/llm-ide-rules/commit/200742d70300942ca1649f316fa2943687179e75))
* expand python and copilot instructions for clarity and conventions ([3be565c](https://github.com/iloveitaly/llm-ide-rules/commit/3be565c3b54b8c2baef158cfa59ca5c46e7f92f3))
* expand test, Alembic, and agent instructions for clarity ([8ffe377](https://github.com/iloveitaly/llm-ide-rules/commit/8ffe377bd3a43af848c612e2cd0d7d4690f764b1))
* **pytest:** update testing rules for integration and route tests ([4c66b9a](https://github.com/iloveitaly/llm-ide-rules/commit/4c66b9a252d0badd5dce076d1b4648ae33977e22))
* update .cursor rules, add dev-in-browser instructions ([95940c3](https://github.com/iloveitaly/llm-ide-rules/commit/95940c31288c63ab8f603a5a41d3f1726c4056b4))
* update code and testing instructions and prompts for clarity ([ea7ba51](https://github.com/iloveitaly/llm-ide-rules/commit/ea7ba5196f526060a0a005a183e96c7acf5a7d0d))
* update coding and test rules for linting, pnpm usage, debugging ([d99576c](https://github.com/iloveitaly/llm-ide-rules/commit/d99576ca2b7dbe450d64e22f3e33ee7efbc9ef5d))
* update coding instructions and revise env var section ([e44b2cc](https://github.com/iloveitaly/llm-ide-rules/commit/e44b2ccb64aa5fc0f5755d4b529bca9ca4f06bde))
* update coding rules and clarify testing, React, and FastAPI guidelines ([1f70e2b](https://github.com/iloveitaly/llm-ide-rules/commit/1f70e2bae10c1a67d41d569e617e42f848e8f460))
* update date formatting and add guidelines for standalone scripts ([d49df7f](https://github.com/iloveitaly/llm-ide-rules/commit/d49df7fadaa3784b0708a117d57496b4e6dcc840))
* update env file naming conventions in secrets.mdc ([57d75f6](https://github.com/iloveitaly/llm-ide-rules/commit/57d75f69f6dd2714577d10438a3bd33801c828cb))
* update integration, python, and standalone script guidelines ([725fa87](https://github.com/iloveitaly/llm-ide-rules/commit/725fa87c4af74e3e68dc7732836a302bac5b562c))
* Update README writing guidelines ([b27f452](https://github.com/iloveitaly/llm-ide-rules/commit/b27f45246add44493d427e0dbe16c970d07dc04d))
* Update README writing guidelines ([b9485aa](https://github.com/iloveitaly/llm-ide-rules/commit/b9485aa6476eab578dbede9f2fc0a17cf066007a))
* update rules and stripe usage in prompts ([8b461f7](https://github.com/iloveitaly/llm-ide-rules/commit/8b461f75a48d4e2cc71657624d52f9611de8e888))

## [0.3.0](https://github.com/iloveitaly/llm-ide-rules/compare/v0.2.1...v0.3.0) (2025-09-24)


### Features

* add support for downloading AGENTS.md files recursively with preserved directory structure ([#25](https://github.com/iloveitaly/llm-ide-rules/issues/25)) ([b92d6d2](https://github.com/iloveitaly/llm-ide-rules/commit/b92d6d22a038c804071aaa019bf8965ae84c6a62))


### Documentation

* add guideline to avoid emojis and update UI assertion advice ([645884c](https://github.com/iloveitaly/llm-ide-rules/commit/645884cb85037a7f41dc5f6e440e37cf754fcbdd))
* clarify Python comment and system package rules in .cursor ([12d5200](https://github.com/iloveitaly/llm-ide-rules/commit/12d52000d028a15f6f743c32c9ceb485ec45e2a4))
* refine instructions on error handling, testing, and Stripe usage ([2c5c176](https://github.com/iloveitaly/llm-ide-rules/commit/2c5c1761dd8e863b27f66ca3a16a54cf5cfa9b3b))
* update readme to reference more LLM tools ([ff265c7](https://github.com/iloveitaly/llm-ide-rules/commit/ff265c73bcf1bac9bf3861810b269bf17465d4ef))

## [0.2.1](https://github.com/iloveitaly/llm-ide-rules/compare/v0.2.0...v0.2.1) (2025-09-15)


### Bug Fixes

* cli script name ([b30448c](https://github.com/iloveitaly/llm-ide-rules/commit/b30448c43baa13886ce5b36e47e54c5bdad2be48))
* update default repo name to iloveitaly/llm-ide-rules ([4251ce7](https://github.com/iloveitaly/llm-ide-rules/commit/4251ce77811caa4247654bcbaaed1db904401192))


### Documentation

* fix typos and clarify Python rules in .cursor configs ([20720f2](https://github.com/iloveitaly/llm-ide-rules/commit/20720f26df1f7d219db08ee9b43232f1abc46d98))
* update README to use llm-ide-rules CLI name and repo ([27f396b](https://github.com/iloveitaly/llm-ide-rules/commit/27f396bbc6640d2597cbfb23546b0884636836f3))

## [0.2.0](https://github.com/iloveitaly/llm-ide-rules/compare/v0.1.0...v0.2.0) (2025-09-15)


### Features

* attempt to use trusted publishers ([0b46019](https://github.com/iloveitaly/llm-ide-rules/commit/0b460192ef1bd548d0cbc1c4a245368cbaedf5b4))


### Documentation

* **stripe-backend:** add Stripe API integration guidelines for Python backend ([fbaef48](https://github.com/iloveitaly/llm-ide-rules/commit/fbaef48f24946907c9342dc67df3b15a4a785a34))
* update rules with python package, alembic and test guidelines ([b8a7952](https://github.com/iloveitaly/llm-ide-rules/commit/b8a79527285dbe664ba27acb213cc26ff13f3250))

## 0.1.0 (2025-08-19)


### Features

* add 'all' option to download both .cursor and .github folders ([e372b95](https://github.com/iloveitaly/llm_ide_rules/commit/e372b954872f6e197dbd4540ecef83fd589b91b8))
* add copilot2cursor script to generate Cursor rules ([c3337fe](https://github.com/iloveitaly/llm_ide_rules/commit/c3337fe402afae7fcc0ee87fb27c5fb9f8fea222))
* add download script for fetching and extracting files ([4c7b164](https://github.com/iloveitaly/llm_ide_rules/commit/4c7b1644125bd6098a5f53be577aef7008e37565))
* add GEMINI.md with updated React & form best practices ([c5e0496](https://github.com/iloveitaly/llm_ide_rules/commit/c5e0496464a67435ec4e95e7ab7cc2d43232a837))
* add script to bundle instruction files for cursor and github ([4884745](https://github.com/iloveitaly/llm_ide_rules/commit/4884745c9be7f88ec0fb744e4d590a571bafa95c))
* add script to download .cursor or .github from repo ([61e37a1](https://github.com/iloveitaly/llm_ide_rules/commit/61e37a191fd10a8aba1d7cc008fce69f464ef92f))
* improve bundling for GitHub instructions and YAML frontmatter ([0f1a939](https://github.com/iloveitaly/llm_ide_rules/commit/0f1a93974e9d2999707e1b484e6ebfa2dc7dd783))
* improve rule bundling headers and clarify shell assumptions ([69c35fd](https://github.com/iloveitaly/llm_ide_rules/commit/69c35fd4a925fda8c2afe04827512a947f151f7d))
* initialize Python package structure and configs ([178165d](https://github.com/iloveitaly/llm_ide_rules/commit/178165d0abd5f5d901b6e30c008075c3d5e0e9a7))
* output Copilot-compatible instructions alongside Cursor rules ([45b5b05](https://github.com/iloveitaly/llm_ide_rules/commit/45b5b05c3cd63611ca6c4604fe823dd001eb44b2))
* standardize header formatting and add section extraction for FastAPI and ReactRouter ([3a773a4](https://github.com/iloveitaly/llm_ide_rules/commit/3a773a4e7d5669cd9d5faae96090a92bd87b07ae))
* support writing prompt files for prompt-only sections ([5da363c](https://github.com/iloveitaly/llm_ide_rules/commit/5da363c7e566fff0ec0c0af8350ee7ccdc3b5cb8))


### Bug Fixes

* exclude .github/workflows from unzip in download.sh ([66b53c8](https://github.com/iloveitaly/llm_ide_rules/commit/66b53c8335cbd1ce9102f0821cefa7c82104bc66))
* handle section header case-insensitivity in explode.py ([2346d70](https://github.com/iloveitaly/llm_ide_rules/commit/2346d70cc7245f7b3b0a195b8040eeac312e9252))
* remove empty frontmatter from prompt rule files ([86c9432](https://github.com/iloveitaly/llm_ide_rules/commit/86c9432decd06c6b60af99df5a192bf0fdf2ac90))
* strip all trailing and leading whitespace from header yaml in write_rule ([64d5d40](https://github.com/iloveitaly/llm_ide_rules/commit/64d5d405ee445357bbd75026c6b6ca739d85d94d))


### Documentation

* add and update coding guidelines for react, typescript, pytest, and react-router ([21bfea7](https://github.com/iloveitaly/llm_ide_rules/commit/21bfea7dd2c811b857802767000e25c7a53fb05e))
* add cursor agent instructions and rules for tests and alembic migrations ([b84b5bf](https://github.com/iloveitaly/llm_ide_rules/commit/b84b5bf188d8d53286fda613e182ed541dd3e142))
* add Cursor rules for FastAPI and React Router code styles ([1f7c118](https://github.com/iloveitaly/llm_ide_rules/commit/1f7c118a5ffa5d6947273580459e4cb7c0230239))
* add FastAPI and TypeScript guidelines, clarify React/Router instructions ([776f5f8](https://github.com/iloveitaly/llm_ide_rules/commit/776f5f84fff4170793f961d4e1135d1990f21e1f))
* add guidance on app commands, jobs, and pytest integration ([72bc6c0](https://github.com/iloveitaly/llm_ide_rules/commit/72bc6c0ef71d61f229938fac7ce17a89c481ef3a))
* add guidelines for managing environment variable secrets ([7657091](https://github.com/iloveitaly/llm_ide_rules/commit/7657091bec4b19f60bea502a1ecca4c58987e23b))
* add instructions for downloading AGENT.md for Amp ([44cf5cf](https://github.com/iloveitaly/llm_ide_rules/commit/44cf5cf2cda94c8a45870208f08d210189044671))
* add instructions for TypeScript file-level docstrings ([f34d8d9](https://github.com/iloveitaly/llm_ide_rules/commit/f34d8d90e949b1476486e770856fb87a87bce5f2))
* add prompts for react-router loader, ts docstrings, and env vars management ([88162cf](https://github.com/iloveitaly/llm_ide_rules/commit/88162cf1b3ef9f5b5705bd7ae9a0d06e9f3ad471))
* add python route test guidelines and update section mapping ([bfccdf3](https://github.com/iloveitaly/llm_ide_rules/commit/bfccdf3d539e24e26e4d2846536be4d7f29d6637))
* add React guidelines to instructions.md ([c4e6e9f](https://github.com/iloveitaly/llm_ide_rules/commit/c4e6e9fb71dcc48e6265b01c55232bab57b8d1fd))
* add rules for fastapi route implementation and route tests ([e540a80](https://github.com/iloveitaly/llm_ide_rules/commit/e540a80ae2594aaedb35b87791085de32cdfa516))
* add section headers to all .mdc and instructions.md files ([e73e749](https://github.com/iloveitaly/llm_ide_rules/commit/e73e749529ae9da33ebf3a0b06d2e1757f15fa77))
* add style preference for function declarations in guides ([18c052d](https://github.com/iloveitaly/llm_ide_rules/commit/18c052d00799b327273ed5c5794e3b86feb63ef3))
* add TODO file with copilot agent execution tasks ([c22f45f](https://github.com/iloveitaly/llm_ide_rules/commit/c22f45f1dce972142eb68e039b3144f87cfd12fb))
* add TypeScript extraction and update instructions for Python and SQLAlchemy ([f271a53](https://github.com/iloveitaly/llm_ide_rules/commit/f271a5397d3767bb612da79248a3daf6dc743961))
* add usage instructions for build process in README ([5dd7107](https://github.com/iloveitaly/llm_ide_rules/commit/5dd7107a524cd22dba5348f1ceb0905de2d361ec))
* adding cursor.directory ([dfa412d](https://github.com/iloveitaly/llm_ide_rules/commit/dfa412d42eff9c1e55328b66b1483bfc1b0ed0df))
* another rule index ([64dc100](https://github.com/iloveitaly/llm_ide_rules/commit/64dc10089586c6a8250245fca6a747b8715ba70a))
* clarify agent instructions for pytest and planning steps ([7e5c604](https://github.com/iloveitaly/llm_ide_rules/commit/7e5c60407974947f13d81a256257289362964e13))
* clarify agent instructions for tests, migrations, typing ([6046325](https://github.com/iloveitaly/llm_ide_rules/commit/6046325cc07f5149133329fd2dde350945bbe241))
* clarify agent test instructions and expand React Router section ([bd7592f](https://github.com/iloveitaly/llm_ide_rules/commit/bd7592f82e84b344b26a1348b81b1237973a7578))
* clarify click usage and heading levels in Python guidelines ([a711b0f](https://github.com/iloveitaly/llm_ide_rules/commit/a711b0fb427b75aa7c8a7d0d74a6a058f9867be6))
* clarify coding standards for naming, spacing, DB, React, mocks ([7902070](https://github.com/iloveitaly/llm_ide_rules/commit/7902070409037155168f4eaada753565dbfdfca7))
* clarify database session usage in pytest integration rules ([5e8955f](https://github.com/iloveitaly/llm_ide_rules/commit/5e8955f0a5261321627240e12c2e8602396d57f3))
* clarify pytest and planning instructions in instructions.md ([683bb17](https://github.com/iloveitaly/llm_ide_rules/commit/683bb17d728b30b78a27cf16d53edb373bb26ddb))
* clarify python comment style, update prompt formats ([d32efaa](https://github.com/iloveitaly/llm_ide_rules/commit/d32efaae33226a79b4cf702b1450547dc960da79))
* clarify secret management descriptions in rules and prompts files ([7ab42a0](https://github.com/iloveitaly/llm_ide_rules/commit/7ab42a07ee7c1980f5e5b036df9ea266c160d9b7))
* clarify secrets section and update heading hierarchy ([223d0fc](https://github.com/iloveitaly/llm_ide_rules/commit/223d0fc3c576bf5e27231d2eefb6f146df6ce0c4))
* clarify test and migration instructions for python and pytest ([db5179a](https://github.com/iloveitaly/llm_ide_rules/commit/db5179a1abad313b82e8eb2238dbf54034d64774))
* clarify to not remove comments in coding instructions ([1cd0077](https://github.com/iloveitaly/llm_ide_rules/commit/1cd00777e8e7f0bfd7d178be78ef23a79cb890f7))
* clarify use of clientLoader and loaderData in React Router ([12860a8](https://github.com/iloveitaly/llm_ide_rules/commit/12860a811b99ff7bf25cfaf07fd2f7513f6cb90b))
* demote React Hook Form section to subheading ([ece38d6](https://github.com/iloveitaly/llm_ide_rules/commit/ece38d6cf4e7e80da4b24a46cb2c2670d1583546))
* enforce not removing existing comments in coding rules ([fff6b90](https://github.com/iloveitaly/llm_ide_rules/commit/fff6b909ee2456d6f3e2699084960aba7f663a0c))
* expand React and TypeScript guidelines, add React Hook Form usage ([031db2e](https://github.com/iloveitaly/llm_ide_rules/commit/031db2ee678d612b5c4a3af3ffb9a0f0a235578b))
* expand README with motivation and change extraction instructions ([434884f](https://github.com/iloveitaly/llm_ide_rules/commit/434884f5e5d086bcc97153765146b7aee4ab941f))
* extend python instructions for datetime and orm usage ([abf27d4](https://github.com/iloveitaly/llm_ide_rules/commit/abf27d4c46bda1982f98c039fdd9d70e3737081d))
* fix AGENT.md download example in README ([8ca6f7b](https://github.com/iloveitaly/llm_ide_rules/commit/8ca6f7b3247ff27f3c48298812ef9039e45170a5))
* fix bullet formatting and add missing description in rules ([91e142a](https://github.com/iloveitaly/llm_ide_rules/commit/91e142a4ba3ac519122147517e6449272c5de930))
* fix markdown link to instructions.md in readme ([1a9b47b](https://github.com/iloveitaly/llm_ide_rules/commit/1a9b47b2b7dc414311c25483c5b3d9110d48ad34))
* improve react rules and add hook form example ([7994b1f](https://github.com/iloveitaly/llm_ide_rules/commit/7994b1fd14d49b489d605a70a8e214413a4a8478))
* new cursor dir ([ff09d71](https://github.com/iloveitaly/llm_ide_rules/commit/ff09d71459f06e5b0bfa101aae687268cf7a440e))
* reorganize fastapi and react router sections for clarity ([bef8ad0](https://github.com/iloveitaly/llm_ide_rules/commit/bef8ad09988759796915b3ebdd9f05ac69c99e0a))
* **rules:** clarify pytest usage, db access, and add troubleshooting tips ([8965c03](https://github.com/iloveitaly/llm_ide_rules/commit/8965c03cfe262f720c95fcbb465306fbec5fcc3a))
* update and add agent, python, and module directory instructions ([8052907](https://github.com/iloveitaly/llm_ide_rules/commit/8052907b2f21f327bb6f45925bc6e6f828cab611))
* update and expand coding guidelines for all languages and frameworks ([668b3d6](https://github.com/iloveitaly/llm_ide_rules/commit/668b3d67d4da55e91783286c558d17fe8f35a26b))
* update and restructure react and react-router instructions ([d592352](https://github.com/iloveitaly/llm_ide_rules/commit/d59235249025652d728e849a91257997afe4157b))
* update codebase instructions for react, fastapi, python, and typescript ([ac98790](https://github.com/iloveitaly/llm_ide_rules/commit/ac9879011e11f4f72e5c74dccd8c4fcb392f42d7))
* update coding guidelines for react-router and typescript ([5b63f1c](https://github.com/iloveitaly/llm_ide_rules/commit/5b63f1cc560fecf1193cd47a17515b91526653d8))
* update coding instructions for FastAPI and React Router ([be44265](https://github.com/iloveitaly/llm_ide_rules/commit/be442657921170771432c6f6a5232ae56274e0df))
* update coding standards and folder structure guidelines ([cc50dff](https://github.com/iloveitaly/llm_ide_rules/commit/cc50dffaa95bd5641c578dc119dfcb0e342a6492))
* update Cursor rules for FastAPI, pytest, and planning ([f626305](https://github.com/iloveitaly/llm_ide_rules/commit/f626305770444266bfe0488b1ea1104a8b298842))
* update dev rules for testing, python usage, and modularity ([76f02d9](https://github.com/iloveitaly/llm_ide_rules/commit/76f02d90f58a8eee3fd53976e448de5a79377b52))
* update example for using DistributionFactory in integration tests ([23b9a6d](https://github.com/iloveitaly/llm_ide_rules/commit/23b9a6d380fb11e65b806b98839ae23253c3c886))
* update instructions and prompts for clarity and route usage ([4cc1fae](https://github.com/iloveitaly/llm_ide_rules/commit/4cc1fae1a8948c59b34a599605e1c5c6f0d231ed))
* update instructions for FastAPI, pytest, alembic, and Copilot ([afa186a](https://github.com/iloveitaly/llm_ide_rules/commit/afa186a7cb78ac458f093b2a2019e0397fbfb884))
* update instructions for pytest asserts and frontend folder structure ([d39e4b2](https://github.com/iloveitaly/llm_ide_rules/commit/d39e4b2e23bf9d469af604a909c00fec69ca77db))
* update instructions for python, pytest, and react router ([29ddd58](https://github.com/iloveitaly/llm_ide_rules/commit/29ddd58c25ced4baa9810bb6f1b6979536cd2e34))
* update instructions with frontend and python guidelines ([d66c4bb](https://github.com/iloveitaly/llm_ide_rules/commit/d66c4bbbedb6a03f6eb78ad22db4a1feffd13a05))
* update monorepo coding and tool instructions for clarity ([55d356e](https://github.com/iloveitaly/llm_ide_rules/commit/55d356e7d692cf5b33a3206c3425c682140418e7))
* update python and react-router rules for clarity and guidance ([54e6514](https://github.com/iloveitaly/llm_ide_rules/commit/54e65143cfba77096460256e9642bead146978c8))
* update React & add TypeScript inst. for project structure ([bf81bb6](https://github.com/iloveitaly/llm_ide_rules/commit/bf81bb6205987347b3c403141bdaa4b43d02badd))
* update React and React Router instructions, add FastAPI Stripe prompt ([9c021a3](https://github.com/iloveitaly/llm_ide_rules/commit/9c021a31d41ab55bdd0623e685e1c87c0b386861))
* update react and react-router rules and typescript docstring meta ([d924ca0](https://github.com/iloveitaly/llm_ide_rules/commit/d924ca0fd2686c7375cb9ee799353a1485907d7b))
* update React rules for hooks, error handling, and conditional rendering ([9aa49b9](https://github.com/iloveitaly/llm_ide_rules/commit/9aa49b9e5d699ead65c383d99476221376255695))
* update readme instructions to use download.sh script ([29247ec](https://github.com/iloveitaly/llm_ide_rules/commit/29247ec42a0c7a423508bef2966f1fecc041b6e5))
* update readme with install instructions and dev section ([fb21cb9](https://github.com/iloveitaly/llm_ide_rules/commit/fb21cb9e036b26105032088941e3a3b315a3f56d))
* update rules for FastAPI, React, Python, and routing ([194d558](https://github.com/iloveitaly/llm_ide_rules/commit/194d55865499a70442f96ae6bab599a95176a5a7))
