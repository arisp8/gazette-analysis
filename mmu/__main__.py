import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], '..')))
sys.path.insert(0, os.path.abspath(os.path.split(sys.argv[0])[0]))
from mmu.automations.loader import Loader
from mmu.automations.researcher import Researcher
from mmu.analysis.analyzer import Analyzer


source = "http://www.et.gr/idocs-nph/search/fekForm.html"

loader = Loader(source)
loader.scrape_pdfs()

researcher = Researcher()
researcher.research()

analyzer = Analyzer()
analyzer.start_analysis()