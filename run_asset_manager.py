import importlib
import asset_manager as am

# importlib needed to run reload in more recent maya verisons
importlib.reload(am)
ui = am.showUI()