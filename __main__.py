from mmu.automations.loader import Loader

source = "http://www.et.gr/idocs-nph/search/fekForm.html"

loader = Loader(source)
loader.scrapePdfs()