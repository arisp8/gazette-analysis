from mmu.automations.loader import Loader
from mmu.automations.researcher import Researcher

source = "http://www.et.gr/idocs-nph/search/fekForm.html"

loader = Loader(source)
loader.scrape_pdfs()

researcher = Researcher(2012, 2017)
researcher.research()
