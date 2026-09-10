"""In-memory Config Studio domain service; no experiment execution capability."""
from dataclasses import replace
from typing import Any,Mapping
from terrario.lab.world_contracts import ConfigurationState,ConfigError,LabConfiguration,canonical_json,config_diff,validate_configuration

class ConfigurationRepository:
    def __init__(self): self._items:dict[str,LabConfiguration]={}
    def save(self,config):
        if config.config_id in self._items: raise ConfigError("silent overwrite prohibited")
        self._items[config.config_id]=config; return config
    def get(self,config_id): return self._items[config_id]
    def edit(self,config_id,reason,**changes): return self.save(self.get(config_id).edit(reason,**changes))
    def transition(self,config_id,state,reason):
        child=self.get(config_id).transition(state,reason); return self.save(replace(child,config_id=f"{config_id}.{state.value.lower()}"))

class ConfigStudioService:
    def __init__(self,config): self._config=config
    @property
    def config(self): return self._config
    def structured(self): return canonical_json(self._config)
    def findings(self): return validate_configuration(self._config)
    def typed_edit(self,reason,**changes): self._config=self._config.edit(reason,**changes); return self._config
    def structured_ui_edit(self,ui_preferences:Mapping[str,Any],reason="UI preferences changed"): return self.typed_edit(reason,ui_preferences=ui_preferences)
    def compare(self,other): return config_diff(self._config,other)
