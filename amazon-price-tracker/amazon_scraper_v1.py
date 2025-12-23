from playwright.sync_api import sync_playwright

def extraer_datos_de_la_pagina(page):
    """
    Esta función busca las tarjetas en la página actual y saca los datos.
    Se llama una vez por cada página que visitamos.
    """
    print("recolectando datos de esta página...")
    
    # Usamos el selector que te funcionó a ti
    cards = page.locator("div[data-component-type='s-search-result']").all()
    
    print(f"   -> He encontrado {len(cards)} productos.")

    for card in cards:
        try:
            # ESTRATEGIA 1: Atributo aria-label
            titulo = card.locator("h2").get_attribute("aria-label")
            
            # ESTRATEGIA 2: Texto normal
            if not titulo:
                titulo = card.locator("h2 a span").first.inner_text()
            # --- 🚫 ZONA DE FILTRADO (EL PORTERO) 🚫 ---
            # Convertimos a minúsculas para comparar mejor
            titulo_lower = titulo.lower()
            
            # Si contiene "patrocinado" o "anuncio", lo saltamos
            if "patrocinado" in titulo_lower or "anuncio" in titulo_lower:
                print(f"   🗑️ Saltando publicidad: {titulo[:20]}...")
                continue  # 'continue' fuerza a saltar al siguiente ciclo del bucle
            # ---------------------------------------------

            # 2. Sacamos el Precio

            # Precio
            try:
                precio = card.locator(".a-price .a-offscreen").first.inner_text()
            except:
                precio = "Sin precio"

            # Imprimimos limpio
            print(f"   ✅ {titulo[:40]}... | 💰 {precio}")
            
        except Exception:
            continue

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        page.goto("https://www.amazon.es")

        # --- GESTIÓN DE PANTALLAS MOLESTAS ---
        # 1. Cookies
        try:
            if page.locator("#sp-cc-rejectall-link").is_visible():
                page.locator("#sp-cc-rejectall-link").click()
            elif page.locator("#sp-cc-accept").is_visible():
                page.locator("#sp-cc-accept").click()
        except:
            pass
        
        # 2. Pantalla "Seguir comprando" (Hueco reservado para el futuro)
        # if page.locator("SELECTOR_AQUI").is_visible(): ...

        # --- BÚSQUEDA ---
        search_term = "Iphone 15"
        print(f"\n🔍 Buscando: {search_term}...\n")
        page.locator("#twotabsearchtextbox").fill(search_term)
        page.locator("#twotabsearchtextbox").press("Enter")
        page.wait_for_selector(".s-main-slot")

        # --- BUCLE DE PAGINACIÓN (EL NÚCLEO) ---
        paginas_totales = 3
        pagina_actual = 1

        while pagina_actual <= paginas_totales:
            print(f"\n--- 📄 PROCESANDO PÁGINA {pagina_actual} ---")
            
            # 1. LLAMAMOS A LA FUNCIÓN DE EXTRAER (Aquí ocurre la magia)
            extraer_datos_de_la_pagina(page)

            # 2. Si ya hemos llegado al límite, paramos
            if pagina_actual == paginas_totales:
                print("Límite de páginas alcanzado.")
                break

            # 3. Intentamos ir a la siguiente
            boton_siguiente = page.locator(".s-pagination-next")

            if boton_siguiente.is_visible() and "s-pagination-disabled" not in boton_siguiente.get_attribute("class"):
                boton_siguiente.click()
                print("➡️ Click en 'Siguiente', cargando...")
                page.wait_for_timeout(4000) # Espera importante para que cargue la nueva página
                pagina_actual += 1
            else:
                print("⛔ No hay botón 'Siguiente' o es la última página.")
                break

        print("\n🏁 Fin del scraping.")
        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    run()