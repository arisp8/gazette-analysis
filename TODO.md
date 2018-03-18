### Optimisation
- [x] Cover cross-platform issues in loader so that it can work in Linux, Windows and macOS
- [x] Try to gather all links when parsing the results pages and then download them faster. In order to do this I must
find a way to locate the files from the Content-Desposition header and use urllib (or something similar) to download
and rename them in a safe way.

### Features
- [x] Use an SQLite database (to allow local saving without a server) and create a handler to insert, update and
delete all needed components (ministers, terms, signatures, files & logs to begin with)
- [x] Model ministry changes along the way, while somehow tracking what sort of differences there are and which
ministries are the predecessors of the current one.
- [x] Create researcher which will be able to:
- [x] Find information about all current ministries and ministers
- [x] Be easily updated when anything is changed
- [x] Fetch and retrieve relevant information given a name of a politician
- [ ] Guarantee that all signing names are extracted when parsing a pdf.
- [ ] When preparing the data for analysis, use the extracted roles and the researched data to make sure the data is accurate.
- [ ] Create tests to ensure that the correct ministry is found for each person.
- [ ] Improve calculations about co-responsibilities.
- [ ] Use a clustering method to find merger candidates.
- [ ] Improve researching by finding ministry changes, which allows us to see a ministry's relations evolve/change through time.
