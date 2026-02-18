import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_diabetes_dataset():
    # Load the diabetes dataset from a CSV file
    df = pd.read_csv('/Users/afonso/sns24/data/diabetes_dataset.csv')
    
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    return df


def tratamento_dados(df):
    df = df.copy()

    # Dictionary mapping for categorical columns
    mappings = {
        'gender': {'Male': 0, 'Female': 1, 'Other': 2},
        'ethnicity': {'White': 0, 'Hispanic': 1, 'Black': 2, 'Asian': 3, 'Other': 4},
        'education_level': {'No formal': 0, 'Highschool': 1, 'Graduate': 2, 'Postgraduate': 3},
        'income_level': {'Low': 0, 'Low-Middle': 1, 'Upper-Middle': 2, 'High': 3},
        'employment_status': {'Employed': 0, 'Unemployed': 1, 'Retired': 2, 'Student': 3},
        'smoking_status': {'Never': 0, 'Former': 1, 'Current': 2},
        'diabetes_stage': {'No Diabetes': 0, 'Pre-Diabetes': 1, 'Type 1': 2, 'Type 2': 3, 'Gestational': 4}
    }

    # Apply mappings to categorical columns
    for col, mapping in mappings.items():
        # Strip whitespace from values before mapping
        df[col] = df[col].str.strip()
        df[col] = df[col].map(mapping).fillna(-1).astype(int)

    # Rename columns to Portuguese
    df.rename(columns={
        'gender': 'género',
        'age': 'idade',
        'hypertension_history': 'histórico_hipertensão',
        'heart_rate': 'frequência_cardíaca',
        'ethnicity': 'étnia',
        'education_level': 'nível_educacional',
        'income_level': 'nível_renda',
        'employment_status': 'status_emprego',
        'smoking_status': 'status_tabagismo',
        'alcohol_consumption_per_week': 'consumo_alcool_semanal',
        'physical_activity_minutes_per_week': 'atividade_física_minutos_semanal',
        'bmi': 'imc',
        'diet_score': 'pontuação_dieta',
        'sleep_hours_per_day': 'horas_sono_diário',
        'screen_time_hours_per_day': 'tempo_tela_horas_diário',
        'family_history_diabetes': 'histórico_familiar_diabetes',
        'cardiovascular_history': 'histórico_cardiovascular',
        'waist_to_hip_ratio': 'relação_cintura_quadril',
        'systolic_bp': 'pressão_sistólica',
        'diastolic_bp': 'pressão_diastólica',
        'cholesterol_total': 'colesterol_total',
        'hdl_cholesterol': 'colesterol_hdl',
        'ldl_cholesterol': 'colesterol_ldl',
        'triglycerides': 'triglicerídeos',
        'glucose_fasting': 'glicose_jejum',
        'glucose_postprandial': 'glicose_pós_prandial',
        'insulin_level': 'nível_insulina',
        'hba1c': 'hba1c',
        'diabetes_risk_score': 'pontuação_risco_diabetes',
        'diabetes_stage': 'estágio_diabetes',
        'diagnosed_diabetes': 'diagnóstico_diabetes'
    }, inplace=True)
    
    return df

if __name__ == "__main__":
    df = load_diabetes_dataset()

    print(df.columns.tolist())

    df = tratamento_dados(df)

    print(df.columns.tolist())

    # print das variáveis numéricas e os seus valores possíveis
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        unique_values = df[col].unique()
        print(f"Coluna: {col}, Valores únicos: {unique_values}")

    # corr_matrix = df.corr(numeric_only=True)
    # f, ax = plt.subplots(figsize=(12, 10))
    # sns.heatmap(corr_matrix, vmax=1.0, vmin=-1.0, square=True, annot=True, linewidths=1, cmap='coolwarm', ax=ax, fmt=".2f", annot_kws={"size": 5})
    # plt.title('Correlation Matrix')
    # plt.xticks(rotation=45, ha="right")
    # plt.yticks(rotation=0)
    # plt.tight_layout()
    # plt.show()