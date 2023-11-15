import taipy as tp
from taipy.core.config import Config
import os 


PATHS = ["./data/final", "./data/logging", "./data/raw", ".data/temp", "./data/temp", "./data/third"]


def assegurar_diretorio(paths):
    print("Verificando diretórios...")
    for path in paths:
        if not os.path.exists(path):
            print("Criando diretórios...")
            os.makedirs(path)


Config.load("taipy-config.toml") # Load TOML file

scenario = Config.scenarios["pipeline"] # Load Scenario


if __name__ == '__main__':
    assegurar_diretorio(PATHS)

    tp.Core().run() # Run Core
  
    # Create Scenario instance based on what was read from TOML file
    scenario = tp.create_scenario(scenario) 

    # Execute
    scenario.submit()

    # Fetch results
    print("Sensibilidade bruto", scenario.sensibilidade_anual.read())
    print("\n")
    print("Resultado", scenario.dataset_pronto_para_transformacao.read())
    print("\n")
    print("Resultado", scenario.dataset_final_csv.read())