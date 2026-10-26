# EDICIÓN COMENTADA PARA LECTURA. Las fuentes ejecutadas y selladas permanecen en la raíz.
# Protocolo histórico v2: usa proxies de alta y disponibilidad del resultado.
# Solo se añaden comentarios: no se han ejecutado instrucciones de esta copia.
"""Fase 4.2: protocolo aproximado v2, trazabilidad y baseline sin tocar prueba."""
from pathlib import Path
import hashlib
import json
import platform
import importlib.metadata

import pandas as pd

from src.features import separate_model_data, FEATURES
from src.splitting import (PROTOCOL_V2, PARTITIONS, add_status_availability,
                          temporal_split, temporal_split_legacy)
from src.baseline import fit_and_validate


PRIMARY_SOURCE = "https://pmc.ncbi.nlm.nih.gov/articles/PMC6297060/"


# Convertir tablas a registros JSON, incluyendo el caso de una partición vacía.
def records(table):
    """JSON estándar, también para la partición vacía de prueba no madura."""
    return table.astype(object).where(table.notna(), None).to_dict("records")


# Guardar metadatos y resultados con formato consistente para su auditoría.
def write_json(path, value):
    # Persistir documentación o metadatos para revisar las decisiones sin volver a ejecutar el modelo.
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def build_protocol(root):
    """Aplica reglas prefijadas y guarda el manifiesto ANTES de entrenar modelos."""
    root = Path(root)
    state_path=root/'reports/estado_protocolo.json'
    # Distinguir resultados ya guardados de una ejecución pendiente antes de continuar.
    if state_path.exists() and json.loads(state_path.read_text(encoding='utf-8')).get('vigente') != PROTOCOL_V2['version']:
        raise RuntimeError('No sobrescribir protocolo vigente con reproducción v2: usar copia histórica aislada.')
    reports = root / "reports"
    history = reports / "historico/protocolo_v1"
    if not (history / "registro_historico.json").is_file():
        raise ValueError("Debe conservarse y verificarse primero el protocolo v1.")
    historical_record = json.loads((history / "registro_historico.json").read_text(encoding="utf-8"))
    for filename, checksum in historical_record["archivos_sha256"].items():
        if hashlib.sha256((history / filename).read_bytes()).hexdigest() != checksum:
            raise ValueError(f"El histórico v1 no coincide con su registro: {filename}")
    preparation = json.loads((reports / "preparacion_resumen.json").read_text(encoding="utf-8"))
    raw_path, prepared_path = root / "data/raw/hotel_bookings.csv", root / "data/processed/hotel_bookings_prepared.csv"
    # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
    assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == preparation["sha256_original"]
    # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
    assert hashlib.sha256(prepared_path.read_bytes()).hexdigest() == preparation["sha256_preparado"]
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    raw = pd.read_csv(raw_path)
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    prepared = pd.read_csv(prepared_path)
    features, target, metadata = separate_model_data(prepared)
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    old_manifest = pd.read_csv(history / "particiones_temporales.csv")
    # Comprobar tamaños esperados para detectar pérdidas de filas o desalineación.
    assert len(raw) == len(features) == len(old_manifest) == 119390 and len(FEATURES) == 14
    # Hacer explícito este invariante: si falla, no se deben interpretar los resultados como válidos.
    assert metadata.meta_row_id.tolist() == old_manifest.meta_row_id.tolist() == raw.index.tolist()
    old_assigned = old_manifest.particion
    pd.testing.assert_series_equal(old_assigned, temporal_split_legacy(metadata), check_names=False)
    metadata = add_status_availability(metadata, raw.reservation_status_date)
    assigned = temporal_split(metadata)
    # La nueva regla permite comprobar el cierre de prueba; para el cierre asumido elegido
    # se mantienen exactamente sus IDs. Ningún registro de la prueba v1 se reutiliza para fit.
    old_test = set(metadata.loc[old_assigned.eq("prueba_reservada"), "meta_row_id"])
    current_test = set(metadata.loc[assigned.eq("prueba_reservada"), "meta_row_id"])
    if old_test != current_test:
        raise ValueError("Cambian los IDs protegidos de prueba; documentar y revisar antes de entrenar.")
    if set(metadata.loc[assigned.isin(["entrenamiento", "validacion"]), "meta_row_id"]) & old_test:
        raise ValueError("Una reserva de prueba histórica ha entrado en desarrollo.")
    rows = []
    for partition in PARTITIONS:
        mask = assigned.eq(partition)
        data = metadata.loc[mask]
        n = int(mask.sum())
        row = {"particion": partition, "registros": n, "no_canceladas": int(target.loc[mask].eq(0).sum()),
               "canceladas": int(target.loc[mask].eq(1).sum()),
               "tasa_cancelacion": float(target.loc[mask].mean()) if n else None,
               "lead_time_mediana": float(features.loc[mask, "lead_time"].median()) if n else None}
        for column, label in [("meta_booking_date_proxy", "proxy"), ("meta_arrival_date", "llegada"),
                              ("meta_label_available_proxy", "disponibilidad_proxy")]:
            dates = pd.to_datetime(data[column])
            row[label + "_min"] = str(dates.min().date()) if n else None
            row[label + "_max"] = str(dates.max().date()) if n else None
        rows.append(row)
    table = pd.DataFrame(rows)
    for name in ["entrenamiento", "validacion", "prueba_reservada"]:
        if not assigned.eq(name).any() or target.loc[assigned.eq(name)].nunique() != 2:
            raise ValueError(f"Partición vacía o con una única clase: {name}")
    train_months = pd.crosstab(features.loc[assigned.eq("entrenamiento"), "hotel"],
        pd.to_datetime(metadata.loc[assigned.eq("entrenamiento"), "meta_arrival_date"]).dt.month).reindex(columns=range(1, 13), fill_value=0)
    # Hacer explícito este invariante: si falla, no se deben interpretar los resultados como válidos.
    assert train_months.gt(0).all().all()
    transition = pd.crosstab(old_assigned, assigned).reindex(columns=PARTITIONS, fill_value=0)
    old_excluded = old_assigned.str.startswith("no_madura")
    reincorporated = old_excluded & assigned.isin(["entrenamiento", "validacion"])
    # Resumir la misma población por grupos y conservar sus denominadores antes de comparar tasas.
    monthly = pd.DataFrame({"grupo_v1": old_assigned.loc[old_excluded],
        "mes_proxy": pd.to_datetime(metadata.loc[old_excluded, "meta_booking_date_proxy"]).dt.to_period("M").astype(str),
        "reincorporada": reincorporated.loc[old_excluded].astype(int)}).groupby(["grupo_v1", "mes_proxy"]).agg(
            reservas=("reincorporada", "size"), reincorporadas=("reincorporada", "sum")).reset_index()
    monthly["pendientes"] = monthly.reservas - monthly.reincorporadas
    recovered_profiles = []
    for name in ["entrenamiento", "validacion"]:
        mask = reincorporated & assigned.eq(name)
        recovered_profiles.append({"destino": name, "reincorporadas": int(mask.sum()),
            "canceladas": int(target.loc[mask].eq(1).sum()), "no_canceladas": int(target.loc[mask].eq(0).sum()),
            "lead_time_mediana": float(features.loc[mask, "lead_time"].median())})
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    old_profile = pd.read_csv(reports / "auditoria_4_1_perfiles_seleccion.csv")
    sensitivity = []
    for close in ["2017-09-01", "2017-09-15", PROTOCOL_V2["assumed_as_of_exclusive"]]:
        q = pd.to_datetime(metadata.loc[old_assigned.eq("prueba_reservada"), "meta_label_available_proxy"])
        sensitivity.append({"corte_exclusivo_escenario": close, "cumplen_proxy": int(q.lt(close).sum()),
                            "no_cumplen_proxy": int(q.ge(close).sum()),
                            "acreditado": False, "seleccionado": close == PROTOCOL_V2["assumed_as_of_exclusive"]})
    report = {"protocolo": PROTOCOL_V2, "fuente_primaria": PRIMARY_SOURCE,
        "fechas_observadas": {"ultima_llegada": str(pd.to_datetime(metadata.meta_arrival_date).max().date()),
            "max_fecha_estado": str(pd.to_datetime(raw.reservation_status_date).max().date()),
            "max_proxy_disponibilidad": str(pd.to_datetime(metadata.meta_label_available_proxy).max().date())},
        "cierre_asumido": PROTOCOL_V2["assumed_as_of_exclusive"], "cierre_acreditado": None,
        "madurez_real_garantizada": False,
        "particiones": records(table), "perfiles_v1_para_comparacion": records(old_profile),
        "antes_apartadas": int(old_excluded.sum()), "reincorporadas": int(reincorporated.sum()),
        "proporcion_reincorporada": float(reincorporated.sum() / old_excluded.sum()),
        "pendientes_v2": int(assigned.str.startswith("no_madura").sum()),
        "perfil_reincorporadas": recovered_profiles,
        "sin_solapamientos": True, "sin_grupos_compartidos": True, "prueba_mismos_ids_v1": True,
        "cobertura_total": len(assigned), "cortes_fijados_antes_de_metricas": True,
        "metricas_v1_obsoletas_para_comparacion_actual": True,
        "sha256_original": preparation["sha256_original"], "sha256_preparado": preparation["sha256_preparado"],
        "meses_entrenamiento_por_hotel": {str(k): {str(m): int(v) for m, v in values.items()} for k, values in train_months.to_dict("index").items()},
        "sensibilidad_cierre_solo_metadatos": sensitivity,
    }
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    pd.DataFrame({"meta_row_id": metadata.meta_row_id, "particion": assigned}).to_csv(reports / "particiones_temporales.csv", index=False)
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    transition.to_csv(reports / "protocolo_4_2_transicion.csv")
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    monthly.to_csv(reports / "protocolo_4_2_apartadas_por_mes.csv", index=False)
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    pd.DataFrame(recovered_profiles).to_csv(reports / "protocolo_4_2_reincorporadas_perfil.csv", index=False)
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    table.to_csv(reports / "protocolo_4_2_particiones.csv", index=False)
    write_json(reports / "division_temporal.json", report)
    write_json(reports / "protocolo_4_2_config.json", {**PROTOCOL_V2,
        "fuente_primaria": PRIMARY_SOURCE, "eleccion": "Antes de entrenar; sin métricas de prueba.",
        "estado": "Protocolo aproximado de fechas registradas; no certifica predicción al crear la reserva."})
    return features, target, metadata, assigned, report


# Ejecutar el baseline bajo el protocolo histórico v2 y exportar sus verificaciones.
def run_protocol(project_root=None):
    root = Path(project_root) if project_root else Path(__file__).resolve().parents[1]
    reports = root / "reports"
    protected = [root / "data/raw/hotel_bookings.csv", root / "data/processed/hotel_bookings_prepared.csv"]
    protected += [reports / name for name in ["fase_3_preparacion.md", "fase_4_baseline.md", "fase_4_1_auditoria.md"]]
    protected += list((reports / "historico/protocolo_v1").glob("*"))
    # Calcular una huella determinista para trazabilidad; no usarla como característica predictiva.
    before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected if p.is_file()}
    features, target, metadata, assigned, report = build_protocol(root)
    # La selección ya se ha guardado. No se toca prueba, ni siquiera transformándola.
    _, metrics, audit, predictions = fit_and_validate(features, target, assigned, transform_test=False)
    predictions.insert(0, "meta_row_id", metadata.loc[assigned.eq("validacion"), "meta_row_id"])
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    predictions.to_csv(reports / "baseline_predicciones_validacion.csv", index=False)
    result = {"protocolo_version": PROTOCOL_V2["version"], "evaluacion": "Solo validación elegible v2",
              "parametros_fijados": audit["parametros"], "metricas": metrics, "auditoria_fit": audit,
              "particiones": report["particiones"], "prueba_evaluada": False,
              "sha256_original": report["sha256_original"], "sha256_preparado": report["sha256_preparado"],
              "cierre_asumido": report["cierre_asumido"], "cierre_acreditado": None,
              "limitacion": "Disponibilidad/creación aproximadas; selección por resultados registrados y predictores no certificados al alta."}
    write_json(reports / "baseline_resultados.json", result)
    previous = json.loads((reports / "historico/protocolo_v1/baseline_resultados.json").read_text(encoding="utf-8"))
    comparison = []
    for version, values in [("v1_historia_no_comparable_como_ranking", previous), ("v2_vigente", result)]:
        for name, row in values["metricas"].items():
            comparison.append({"protocolo": version, "modelo": name,
                **{k: v for k, v in row.items() if k != "matriz_confusion"}})
    # Guardar esta tabla como evidencia reproducible de la población y fase indicadas.
    pd.DataFrame(comparison).to_csv(reports / "protocolo_4_2_comparacion_descriptiva.csv", index=False)
    make_figures(reports, result, report)
    for filename, checksum in before.items():
        # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
        assert hashlib.sha256((root / filename).read_bytes()).hexdigest() == checksum, filename
    references = json.loads((reports / "verificacion_referencias.json").read_text(encoding="utf-8"))["antes"]
    verified, unavailable = 0, 0
    for filename, expected in references.items():
        path = Path(filename)
        if not path.is_file():
            unavailable += 1
            continue
        with path.open("rb") as file:
            # La huella debe conservarse: cualquier cambio de datos o evidencia detiene la comprobación.
            assert hashlib.file_digest(file, "sha256").hexdigest() == expected
        verified += 1
    verification = {"protocolo_version": PROTOCOL_V2["version"], "original_y_preparado_intactos": True,
        "historico_v1_intacto": True, "archivos_protegidos_sha256": before,
        "referencias_sin_cambios": verified, "referencias_no_disponibles": unavailable,
        "transformadores_fit_solo_entrenamiento": True, "test_transformado": False,
        "test_predicho": False, "test_evaluado": False, "ids_prueba_iguales_v1": True,
        "umbral": 0.5, "hiperparametros_optimizados": False, "predictores": FEATURES,
        "versiones": {"python": platform.python_version(), **{name: importlib.metadata.version(name) for name in ["pandas", "numpy", "scikit-learn"]}}}
    write_json(reports / "baseline_verificacion.json", verification)
    write_json(reports / "protocolo_4_2_verificacion.json", verification)
    write_json(reports / "estado_protocolo.json", {
        "vigente": PROTOCOL_V2["version"], "fase": "4.2", "manifiesto": "reports/particiones_temporales.csv",
        "metricas_vigentes": "reports/baseline_resultados.json", "historico": "reports/historico/protocolo_v1/",
        "metricas_fases_4_y_4_1_obsoletas_para_comparar_modelos": True,
        "fase_5_iniciada": False, "uso_admisible": "Comparación académica exploratoria bajo supuestos; no validación estricta al crear la reserva."})
    write_report(root, report, result, comparison)
    return report, result


# Representar las tablas de esta fase sin usar el gráfico para ajustar el modelo.
def make_figures(reports, result, report):
    import os
    os.environ.setdefault("MPLCONFIGDIR", str(reports.parent / ".jupyter_runtime/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_theme(style="whitegrid")
    # Crear una figura descriptiva; sus ejes y títulos deben identificar población y versión del protocolo.
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), layout="constrained")
    for ax, (name, values) in zip(axes, result["metricas"].items()):
        sns.heatmap(values["matriz_confusion"], annot=True, fmt="d", cmap="Blues", cbar=False,
            xticklabels=["No cancela", "Cancela"], yticklabels=["No cancela", "Cancela"], ax=ax)
        ax.set(title="Mayoritario v2" if name == "mayoritario" else "Logística v2 (umbral 0,5)", xlabel="Predicción", ylabel="Clase real")
    fig.savefig(reports / "figures/protocolo_4_2_confusion_validacion.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    recovery = pd.DataFrame(report["perfil_reincorporadas"])
    pending = [next(row["registros"] for row in report["particiones"] if row["particion"] == "no_madura_" + name) for name in recovery.destino]
    # Crear una figura descriptiva; sus ejes y títulos deben identificar población y versión del protocolo.
    fig, ax = plt.subplots(figsize=(8, 4.2), layout="constrained")
    ax.barh(["Apartadas v1: entrenamiento", "Apartadas v1: validación"], recovery.reincorporadas, label="Reincorporadas v2", color="#4477AA")
    ax.barh(["Apartadas v1: entrenamiento", "Apartadas v1: validación"], pending, left=recovery.reincorporadas, label="Siguen pendientes", color="#CC6677")
    ax.set(title="Destino de las 30.386 reservas apartadas", xlabel="Registros")
    ax.legend()
    fig.savefig(reports / "figures/protocolo_4_2_reincorporacion.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


# Redactar tablas, metodología y limitaciones desde resultados calculados o guardados.
def write_report(root, protocol, result, comparison):
    from src.audit_baseline import _markdown_table
    partitions = pd.DataFrame(protocol["particiones"])
    previous = pd.DataFrame(comparison)
    current = result["metricas"]["regresion_logistica"]
    tn, fp = current["matriz_confusion"][0]
    fn, tp = current["matriz_confusion"][1]
    history = root / "reports/historico/protocolo_v1"
    old = json.loads((history / "baseline_resultados.json").read_text(encoding="utf-8"))
    # Leer las columnas y filas solicitadas; los filtros de esta llamada determinan la población disponible.
    monthly = pd.read_csv(root / "reports/protocolo_4_2_apartadas_por_mes.csv")
    monthly["trimestre_proxy"] = pd.PeriodIndex(monthly.mes_proxy, freq="M").asfreq("Q").astype(str)
    # Resumir la misma población por grupos y conservar sus denominadores antes de comparar tasas.
    quarterly = monthly.groupby(["grupo_v1", "trimestre_proxy"])[["reservas", "reincorporadas", "pendientes"]].sum().reset_index()
    source_note = f"""# Fuente primaria y alcance de la investigación temporal

[Hotel booking demand datasets — Antonio, de Almeida y Nunes](https://pmc.ncbi.nlm.nih.gov/articles/PMC6297060/), DOI 10.1016/j.dib.2018.11.126, disponible en línea el 29/11/2018.

El artículo define ReservationStatusDate como fecha del último estado. También describe una recuperación de valores del registro de cambios referida, cuando existe, al día anterior a la llegada. Eso no acredita una versión inicial de todos los predictores. La fecha de publicación no equivale al cierre operativo ni a una extracción con integridad garantizada del CSV local.

La consulta no permite acreditar un as_of_date del PMS o un log de publicación de etiquetas. Por ello se adopta **01/12/2018 exclusivamente como corte retrospectivo asumido**: inicio del mes siguiente a la referencia pública. No se deriva del máximo de prueba, no es un hecho sobre el hotel y no acredita seguimiento exhaustivo. La similitud de estructura/conteos no prueba identidad bit a bit con los archivos originales publicados.
"""
    # Persistir documentación o metadatos para revisar las decisiones sin volver a ejecutar el modelo.
    (root / "reports/protocolo_4_2_fuentes.md").write_text(source_note, encoding="utf-8")
    text = f"""# Fase 4.2 — Corrección del protocolo temporal y validación de datos

Fecha: 18 de octubre de 2026. Versión activa: **{PROTOCOL_V2['version']}**. Se termina exclusivamente la fase 4.2. Las tablas generadas usan punto decimal y coma de miles. No se entrenan algoritmos avanzados, optimizan parámetros ni selecciona umbral final.

## 1. Alcance y problemas del protocolo v1

Se revisaron fase_3_preparacion.md, fase_4_baseline.md, fase_4_1_auditoria.md, splitting.py, baseline.py y audit_baseline.py. V1 mezclaba una cota basada en salida prevista y estado final, que retrasaba cancelaciones ya fechadas, con prueba sin cierre global. Sus 30.386 apartadas tenían composición y antelación distintas. La selección por seguimiento limitaba la interpretación de métricas y faltaba una fecha de observación de resultados explícita.

La corrección reduce una exclusión innecesaria y hace explícita la protección de prueba. **No transforma este archivo en una evaluación temporal estricta:** siguen faltando logs de alta, versiones iniciales e ingestión. La modalidad seleccionada es una simulación retrospectiva de disponibilidad registrada, bajo supuestos expresos.

## 2. Cuatro fechas y evidencia

| Concepto | Uso |
|---|---|
| Alta aproximada | llegada prevista − lead_time. Se usa para ordenar cohortes, sin hora ni historial del alta. |
| Llegada prevista | calendario del viaje, distinto del alta y del resultado. Puede ser posterior al corte aun si ya se registró cancelación. |
| Disponibilidad aproximada de resultado | fecha del último estado + un día de margen. No acredita cuándo se conoció/publicó realmente el resultado. |
| Cortes de decisión/observación | 01/07/2016 para fit; 01/01/2017 para validación previa a prueba; 01/12/2018 como cierre retrospectivo asumido de prueba. |

La semántica y la limitación de snapshots se contrastaron en la [fuente primaria]({PRIMARY_SOURCE}). El estado fechado solo se usa como metadato: no es predictor, ni se codifica o imputa en X. La fuente no permite certificar que los 14 campos sean valores del instante inicial. Consultar [nota de fuentes](protocolo_4_2_fuentes.md).

**Tres conceptos de cierre que no deben confundirse:**

- Máximos observados del CSV: llegada {protocol['fechas_observadas']['ultima_llegada']}, último estado {protocol['fechas_observadas']['max_fecha_estado']}, proxy de disponibilidad {protocol['fechas_observadas']['max_proxy_disponibilidad']}.
- Cierre asumido: corte exclusivo **01/12/2018**, anclado al mes siguiente a la publicación de la referencia (29/11/2018), no elegido por métricas o por el último caso de prueba.
- Cierre realmente acreditado del PMS/local: **desconocido**. Publicación y máximo de fechas no acreditan integridad del seguimiento, ingestión o extracción.

La fecha asumida no se presenta como histórica del hotel. Permite un escenario retrospectivo reproducible con margen posterior a los estados observados. El hecho de pasar su comprobación matemática no garantiza que no falten reservas o actualizaciones.

## 3. Alternativas consideradas antes de ajustar el baseline

| Alternativa | Valoración |
|---|---|
| Mantener max(salida prevista, estado)+1 | Retrasa incluso cancelaciones anteriores; no resuelve cierre de prueba. Se conserva solo para historia. |
| Añadir todas las apartadas y usar sus resultados finales en cada corte | Rechazada: incorporaría etiquetas posteriores a decisiones de entrenamiento/selección. |
| Dividir solo por llegada | No reproduce predicción al alta: puede entrenar con resultados posteriores al proxy de reservas evaluadas. Cambiaría el objetivo de evaluación. |
| Limitar lead_time para conseguir cohortes cerradas | Podría servir con un horizonte real de negocio y seguimiento prefijado. No se impone ahora un horizonte arbitrario que retire reservas difíciles. |
| Cohortes completas por alta con seguimiento acreditado | Preferible para validación estricta, pero requiere logs/fechas de cierre y datos adicionales; algunas cohortes observadas tienen estados hasta 2017. |
| Estado fechado + margen, con cierre declarado y pendientes explícitas | Seleccionada como aproximación disponible, manteniendo cortes y prueba; se reconoce selección por resultados registrados y riesgo de instantánea. |

No se tomó la decisión mirando métricas del nuevo baseline o de prueba. Las reglas, manifestación de supuestos y asignaciones se guardaron primero.

## 4. Reglas definitivas para este ejercicio aproximado

`meta_label_available_proxy = reservation_status_date + 1 día`. El margen fijo no se aprende ni se ajusta. `meta_label_available_after` del CSV preparado conserva la cota v1 como metadato histórico y **no dirige la división v2**.

- Entrenamiento: proxy de alta < 01/07/2016 y disponibilidad proxy < 01/07/2016.
- Validación: 01/07/2016 <= proxy de alta < 01/01/2017 y disponibilidad proxy < 01/01/2017.
- Prueba reservada: proxy de alta >= 01/01/2017 y disponibilidad proxy < 01/12/2018 asumido.
- Si una fila no cumple disponibilidad al corte que le corresponde, se asigna a no_madura_entrenamiento, no_madura_validacion o no_madura_prueba. Estos nombres significan no elegible según el proxy, no desconocimiento real demostrado.

Las desigualdades son estrictas. Un estado del día inmediatamente anterior al corte puede seguir pendiente por el margen, deliberadamente conservador. No se añaden a entrenamiento etiquetas fechadas después del corte. No se desplazan pendientes a otros periodos para aprovechar sus resultados futuros. No se permite solapamiento de IDs o grupos exactos. Las fechas de llegada sí pueden superponerse, porque una reserva para una llegada futura puede haberse cancelado antes de entrenar.

## 5. Tamaños, fechas reales y clases

{_markdown_table(partitions[['particion','registros','no_canceladas','canceladas','tasa_cancelacion','lead_time_mediana']], percentages=['tasa_cancelacion'], integers=['registros','no_canceladas','canceladas'])}

{_markdown_table(partitions[['particion','proxy_min','proxy_max','llegada_min','llegada_max','disponibilidad_proxy_max']])}

Se conservan **119.390 filas**, sin modificar ni original ni preparado. Entrenamiento representa los doce meses de llegada en ambos hoteles, aunque no es una muestra completa de todas las altas. El intervalo de proxy anterior a 2015 no representa cobertura íntegra de ese periodo: el archivo está seleccionado por llegadas.

Prueba mantiene exactamente los **26.565 IDs** de v1. Ninguno pasa a desarrollo. La regla de cierre se aplica aunque, con el supuesto elegido, no quede ningún caso pendiente en prueba. Esto no autoriza una evaluación de prueba todavía; aquí solo se auditan tamaños, fechas y clases permitidas.

## 6. Qué ocurre con las 30.386 apartadas

Se reincorporan **{protocol['reincorporadas']:,} ({protocol['proporcion_reincorporada']:.2%})** y permanecen pendientes **{protocol['pendientes_v2']:,}**. El desglose es:

{_markdown_table(pd.DataFrame(protocol['perfil_reincorporadas']), integers=['reincorporadas','canceladas','no_canceladas'])}

El resto es 12.089 del periodo de entrenamiento y 8.475 del de validación. La tabla de transición completa está en protocolo_4_2_transicion.csv. La distribución mensual de las apartadas está en protocolo_4_2_apartadas_por_mes.csv; resumen por trimestre:

{_markdown_table(quarterly, integers=['reservas','reincorporadas','pendientes'])}

V1 había apartado reservas con mediana de antelación 200 días frente a 55 en entrenamiento, y 161 frente a 24 en validación. En v2 las medianas de las incluidas son 68 y 37, mientras las pendientes siguen en 185 y 163 días. **El sesgo no desaparece.** La nueva inclusión favorece cancelaciones registradas pronto: las 4.086 añadidas a validación son canceladas, y casi todas las añadidas a entrenamiento también. Por tanto, la prevalencia de validación cambia del 26.17% al 42.84%, no por el algoritmo sino por población/disponibilidad.

La regla de observación es más coherente con un sistema que solo puede aprender resultados registrados, pero la población con resultado observado a tiempo no es la cohorte completa de reservas. Cancelaciones tempranas y estancias aún abiertas tienen mecanismos de disponibilidad diferentes. No se afirma haber corregido toda censura/supervivencia; ni se interpretará una mejora de métricas como utilidad de negocio recuperada.

## 7. Comprobaciones de disponibilidad y cierre

Cada resultado usado en fit o selección cumple la fecha proxy antes de su corte. Se verifica también disponibilidad posterior al proxy de alta, fechas válidas, alineación de filas, unicidad de asignación y grupos, y condición de prueba. Eso valida la regla implementada, no la disponibilidad real sin logs.

Sensibilidad de prueba usando solo metadatos, sin cambiar la regla seleccionada por esos conteos:

{_markdown_table(pd.DataFrame(protocol['sensibilidad_cierre_solo_metadatos']), integers=['cumplen_proxy','no_cumplen_proxy'])}

Estas cifras se refieren a estado+1, no a salida prevista+estado de la auditoría anterior. No se convierten máximos o escenarios en cierre acreditado. La instantánea de predictores puede ser posterior al alta; la referencia primaria refuerza esta advertencia. La semilla o el aislamiento de preprocesadores no resuelven esa limitación de datos.

## 8. Baseline recalculado únicamente en validación v2

Mismo pipeline, 14 predictores y configuración: mediana, escalado, categoría de ausencia y OneHotEncoder con desconocidas ignoradas; LogisticRegression(C=1, solver=lbfgs, max_iter=2000, class_weight=None, random_state=42), umbral 0.5. No se optimizan hiperparámetros ni umbral. La reproducción verifica estadísticas, vocabularios y número de filas de fit exclusivamente contra entrenamiento.

Fit: {result['auditoria_fit']['n_train_fit']:,} filas. Validación: {result['auditoria_fit']['n_valid_evaluadas']:,}. Iteraciones hasta converger: {result['auditoria_fit']['iteraciones_logistica'][0]}. Prueba no se transforma, predice o evalúa en esta ejecución. No se serializan modelos.

{_markdown_table(previous)}

**La tabla es una comparación descriptiva de protocolos, no un ranking de algoritmos. Las métricas v1 quedan obsoletas para comparar modelos sobre v2.** Cambian entrenamiento, prevalencia y población evaluada, mientras el algoritmo permanece fijo. Los umbrales explorados en 4.1 tampoco se trasladan como decisiones al protocolo nuevo.

Matriz de logística v2, filas reales y columnas predichas:

| Real / predicción | No cancela | Cancela |
|---|---:|---:|
| No cancela | {tn:,} | {fp:,} |
| Cancela | {fn:,} | {tp:,} |

Precision {current['precision']:.2%}, recall {current['recall']:.2%} y ROC-AUC {current['roc_auc']:.4f} se refieren exclusivamente a la validación elegible de esta aproximación. No certifican capacidad al alta ni calibración, rentabilidad o efecto causal de acciones. [Matrices de validación](figures/protocolo_4_2_confusion_validacion.png) y [destino de apartadas](figures/protocolo_4_2_reincorporacion.png).

## 9. Trazabilidad, cambios y pruebas

- splitting.py contiene el protocolo v2 vigente y temporal_split_legacy explícito para reproducir v1.
- temporal_protocol.py implementa/reproduce fase 4.2; tests/test_temporal_protocol.py añade pruebas de fronteras, margen, cierre de prueba, grupos, alineación, errores y no mutación.
- reports/particiones_temporales.csv y division_temporal.json son v2; estado_protocolo.json identifica la versión vigente.
- Cinco archivos de resultados/manifiesto v1 y sus hashes están en reports/historico/protocolo_v1. Los informes de fases anteriores conservan su contenido histórico. Métricas y predicciones v2 ocupan los nombres activos, con versión explícita en JSON.
- baseline.py comparte fábrica y fit, pero la carga/reporte del notebook histórico usa v1. Sus reejecuciones se escriben en historico/protocolo_v1/reproduccion, preservando los cinco archivos congelados y sus huellas. audit_baseline.py lee el histórico para mantener reproducible 4.1. El notebook baseline.ipynb conserva salidas históricas y se anota su versión; su código de rutas se adapta sin reejecutar el análisis anterior.
- El nuevo notebook protocolo_temporal.ipynb presenta y ejecuta v2; README documenta resultados, límites y reproducción. No se modifican las dependencias ni el CSV preparado.

Se ejecutan pruebas automatizadas de v1 y v2, verificaciones de integridad y de fit solo en entrenamiento. El registro técnico está en protocolo_4_2_verificacion.json y baseline_verificacion.json. La fuente externa se documenta separadamente, sin copiar datos o código del artículo.

## 10. Limitaciones pendientes y autorización de fase 5

1. No hay cierre operativo acreditado ni primera disponibilidad de resultados. El cierre público asumido permite un ejercicio retrospectivo, no una garantía de exhaustividad del PMS.
2. El alta es aproximada y no hay historial de valores iniciales. La preparación de la fuente no certifica la disponibilidad de los 14 predictores al alta. Mantenerlos conserva comparabilidad de diseño, pero no convierte el modelo en desplegable.
3. Quedan 20.564 pendientes de decisión temporal; la evaluación observada está condicionada a disponibilidad y contiene sesgo. No se reconstruyen reservas con llegadas fuera de la extracción ni IDs reales de cliente/reserva.
4. El EDA previo vio el archivo completo; los duplicados pueden sobreponderar patrones aunque no crucen conjuntos. No se afirma evaluación independiente ni ausencia total de fuga temporal.

**Puede plantearse fase 5 solo como comparación académica exploratoria bajo este contrato aproximado, con estas mismas particiones y evaluación en validación, si el usuario la autoriza.** Para afirmar validez operacional al crear una reserva se requieren datos iniciales y seguimiento acreditado; eso sigue pendiente y no se suple con mejores métricas. Se deja prueba protegida para una evaluación final autorizada, sujeta a esas limitaciones.

**Fin de fase 4.2. No se avanza a fase 5.**
"""
    # Persistir documentación o metadatos para revisar las decisiones sin volver a ejecutar el modelo.
    (root / "reports/fase_4_2_protocolo_temporal.md").write_text(text, encoding="utf-8")


# Ejecutar la entrada principal solo al invocar este archivo como script.
if __name__ == "__main__":
    protocol, result = run_protocol()
    print(json.dumps({"version": PROTOCOL_V2["version"], "reincorporadas": protocol["reincorporadas"],
                      "pendientes": protocol["pendientes_v2"], "metricas": result["metricas"],
                      "prueba_evaluada": False}, ensure_ascii=False, indent=2))
