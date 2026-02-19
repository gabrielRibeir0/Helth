import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_diabetic_data(file_path):
    """Carrega o dataset de diabetes a partir de um arquivo CSV."""
    try:
        data = pd.read_csv(file_path, na_values=["?"], keep_default_na=True)
        print(f"Dataset carregado com sucesso. Número de registros: {len(data)}")
        return data
    except FileNotFoundError:
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao carregar o dataset: {e}")

def preprocess_diabetic_data(data):
    """Substitui marcadores '?' por valores ausentes reais para análise de missing values."""
    if data is None:
        return None

    processed_data = data.copy()
    processed_data.columns = processed_data.columns.str.strip()

    object_columns = processed_data.select_dtypes(include=["object", "string"]).columns
    for column in object_columns:
        processed_data[column] = (
            processed_data[column]
            .astype("string")
            .str.strip()
            .replace(["?", "None"], pd.NA)
        )

    mapping = {
        'race': {
            'Caucasian': 0,
            'AfricanAmerican': 1,
            'Asian': 2,
            'Hispanic': 3,
            'Other': 4
        },
        'gender': {
            'Male': 0,
            'Female': 1,
            'Unknown/Invalid': 2
        },
        'age': {
            '[0-10)': 0,
            '[10-20)': 1,
            '[20-30)': 2,
            '[30-40)': 3,
            '[40-50)': 4,
            '[50-60)': 5,
            '[60-70)': 6,
            '[70-80)': 7,
            '[80-90)': 8,
            '[90-100)': 9
        },
        'admission_type_id': {
            1: 0,  # Emergency
            2: 1,  # Urgent
            3: 2,  # Elective
            4: 3,  # Newborn
            5: 4,  # Not Available
            6: 5,  # Trauma Center
            7: 6,  # Not Mapped
            8: 7   # Unknown
        },
        'max_glu_serum': {
            'Norm': 0,
            '>200': 1,
            '>300': 2
        },
        'A1Cresult': {
            'Norm': 0,
            '>7': 1,
            '>8': 2
        },
        'metformin': {
            'No': 0, # drug was not prescribed
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'repaglinide': {
            'No': 0, # drug was not prescribed
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'nateglinide': {
            'No': 0, # drug was not prescribed
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'chlorpropamide': {
            'No': 0, # drug was not prescribed
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'glimepiride': {
            'No': 0, # drug was not prescribed
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'acetohexamide': {
            'No': 0, # drug was not prescribed
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'glipizide': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'glyburide': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'tolbutamide': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'pioglitazone': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'rosiglitazone': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'acarbose': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3        },
        'miglitol': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'troglitazone': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'tolazamide': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'examide': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'citoglipton': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'insulin': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3        },
        'glyburide-metformin': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'glipizide-metformin': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'glimepiride-pioglitazone': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'metformin-rosiglitazone': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3
        },
        'metformin-pioglitazone': {
            'No': 0,
            'Steady': 1,
            'Up': 2,
            'Down': 3        },
        'change': {
            'No': 0,
            'Ch': 1
        },
        'diabetesMed': {
            'No': 0,
            'Yes': 1
        }
    }

    for column, map_dict in mapping.items():
        if column in processed_data.columns:
            normalized_map = {str(key).strip(): value for key, value in map_dict.items()}
            processed_data[column] = (
                processed_data[column]
                .astype("string")
                .str.strip()
                .map(normalized_map)
                .fillna(-1)  # Marca valores não mapeados como -1
                .astype(int)
            )

    processed_data = processed_data.drop(columns=["payer_code", "medical_specialty", "readmitted", "weight", "examide", "citoglipton"], errors="ignore")

    # print("Pré-processamento concluído: '?' convertido para missing values.")
    return processed_data

if __name__ == "__main__":
    # Exemplo de uso
    file_path = "/Users/afonso/sns24/data/diabetic_data.csv"  
    diabetic_data = load_diabetic_data(file_path)
    if diabetic_data is not None:
        diabetic_data = preprocess_diabetic_data(diabetic_data)
        diabetic_data.to_csv("diabetic_data_processed.csv", index=False)
        print(diabetic_data.head())

        numeric_data = diabetic_data.select_dtypes(include=["number"])
        corr_matrix = numeric_data.corr()

        f, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr_matrix, vmax=1.0, vmin=-1.0, square=True, annot=True, linewidths=1, cmap='coolwarm', ax=ax, fmt=".2f", annot_kws={"size": 5})
        plt.title('Correlation Matrix')
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.show()
