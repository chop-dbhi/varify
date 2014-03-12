# Contributing

First off, thank you for considering a contribution! Before you submit any code, please read the following Developer's Certificate of Origin (DCO):

```
By making a contribution to the Cilantro project ("Project"),
I represent and warrant that:

a. The contribution was created in whole or in part by me and I have the right
to submit the contribution on my own behalf or on behalf of a third party who
has authorized me to submit this contribution to the Project; or

b. The contribution is based upon previous work that, to the best of my
knowledge, is covered under an appropriate open source license and I have the
right and authorization to submit that work with modifications, whether
created in whole or in part by me, under the same open source license (unless
I am permitted to submit under a different license) that I have identified in
the contribution; or

c. The contribution was provided directly to me by some other person who
represented and warranted (a) or (b) and I have not modified it.

d. I understand and agree that this Project and the contribution are publicly
known and that a record of the contribution (including all personal
information I submit with it, including my sign-off record) is maintained
indefinitely and may be redistributed consistent with this Project or the open
source license(s) involved.
```

This DCO simply certifies that the code you are submitting abides by the clauses stated above. To comply with this agreement, all commits must be signed off with your legal name and email address.

## Logistics

- If you do not have write access to the repo (i.e. not a core contributor), create a fork of Varify
- Branches are used to isolate development and ensure clear and concise intent of the code. Always do your work in a branch off the `master` branch. Name the branch after the issue and number, e.g. `issue-123`. If there is no issue number, [please create one first](https://github.com/cbmi/varify/issues/) before starting your work.
- If working on existing files, ensure the coding style is kept consistent with the code around it. If creating new files or you are unsure of a pattern or preference please consult the [style guides](https://github.com/cbmi/style-guides/).

## Source Code

### *Script

Some code has been done in CoffeeScript, however the decision has been made to port over code to JavaScript. All new code is to be written in JavaScript and any heavy refactors of existing files should be done in JavaScript. The repository has a `.jshintrc` file that will enforce certain rules and conventions on the JavaScript source code. Files should not have any JSHint warnings when being committed. 

### Python

Python code should adhere to (PEP8)[http://legacy.python.org/dev/peps/pep-0008/] and should pass [flake8](https://flake8.readthedocs.org/en/2.0/) without errors or warnings. Any code that fails to pass flake8 will cause the build to fail and will not be considered for merge until the flake8 errors are resolved and the build is passing. 

## Modules

Follow the conventions [outlined in Cilantro](https://github.com/cbmi/cilantro/blob/master/CONTRIBUTING.md#modules).

## Testing

Pre-requisite for testing:

- memcached running on 127.0.0.1:11211

Install test dependencies:

```
pip install -r requirements.txt
```

Run the test suite:

```
python test_suite.py
```
