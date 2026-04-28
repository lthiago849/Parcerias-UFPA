from typing import Optional

def transformar_em_array(texto: Optional[str]) -> list[str]:
    if not texto:
        return [] 
    return [item.strip() for item in texto.split(",") if item.strip()]