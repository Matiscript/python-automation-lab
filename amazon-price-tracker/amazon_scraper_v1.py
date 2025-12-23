from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        page.goto("https://www.amazon.es")

        # --- COOKIES (Tu versión mejorada) ---
        try:
            if page.locator("#sp-cc-rejectall-link").is_visible():
                page.locator("#sp-cc-rejectall-link").click()
            elif page.locator("#sp-cc-accept").is_visible():
                page.locator("#sp-cc-accept").click()
        except:
            pass
        # -------------------------------------

        # Búsqueda
        search_term = "Iphone 15"
        page.locator("#twotabsearchtextbox").fill(search_term)
        page.locator("#twotabsearchtextbox").press("Enter")
        page.wait_for_selector(".s-main-slot")

        print(f"\n🔍 Buscando resultados para: {search_term}...\n")

        # AQUÍ ESTÁ LA MAGIA: Cogemos TODOS los resultados
        # Usamos el selector genérico de 'tarjeta de producto'
        cards = page.locator("div[data-component-type='s-search-result']").all()

        print(f"He encontrado {len(cards)} posibles productos. Analizando los primeros 5...")

        count = 0
        for card in cards:
            if count >= 5: break 

            try:
                # ESTRATEGIA 1: Intentamos leer el atributo oculto (tu descubrimiento)
                titulo = card.locator("h2").get_attribute("aria-label")
                
                # ESTRATEGIA 2: Si el atributo está vacío, buscamos el texto normal de toda la vida
                if not titulo:
                    titulo = card.locator("h2 a span").first.inner_text()

                # Precio (igual que antes)
                precio = card.locator(".a-price .a-offscreen").first.inner_text()

                print(f"✅ {titulo[:40]}... | 💰 {precio}")
                count += 1
                
            except Exception as e:
                # Si falla, es que no era un producto válido
                continue

        print("\n🏁 Fin del scraping.")
        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    run()