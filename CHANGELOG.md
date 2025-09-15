# Changelog

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
