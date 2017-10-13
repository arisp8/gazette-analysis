### Optimisation
- [ ] Cover cross-platform issues in loader so that it can work in Linux, Windows and macOS
- [ ] Try to gather all links when parsing the results pages and then download them faster. In order to do this I must
find a way to locate the files from the Content-Desposition header and use urllib (or something similar) to download
and rename them in a safe way.

### Features
- [ ] Use an SQLite database (to allow local saving without a server) and create a controller to insert, update and
delete all needed components (ministers, terms, signatures, files & logs to begin with)
- [ ] Create researcher which will be able to:
- [-] Find information about all current ministries and ministers
- [-] Be easily updated when anything is changed
- [-] Fetch and retrieve relevant information given a name of a politician

#### Further todos:
- [ ] Find all @TODO comments and improve or fix the code
- [ ] Code cleanup in loader to make it easier to read and understand

