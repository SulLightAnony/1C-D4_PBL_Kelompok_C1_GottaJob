from playwright.sync_api import sync_playwright
import time
import random
import re
import html as html_module


class GlintsScraper:
    def __init__(self):
        print(" Inisialisasi Mesin Playwright (Glints - Mode Headless)...")
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=True,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                "--window-size=1920,1080",
            ]
        )

        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            screen={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="id-ID",
            color_scheme="light",
            has_touch=False,
            is_mobile=False,
        )

        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['id-ID','id','en-US','en']});
            window.chrome = {runtime: {}};
        """)

        self.page = self.context.new_page()
        self.page.set_default_timeout(30000)

    # ------------------------------------------------------------------
    def _teks_bersih(self, locator):
        try:
            if locator.count() > 0:
                t = locator.first.inner_text().strip()
                if t:
                    # Lokalisasi istilah waktu
                    t = t.replace("/month", "/Bulan").replace("/year", "/Tahun").replace("/day", "/Hari")
                    t = t.replace(" month", " Bulan").replace(" year", " Tahun").replace(" day", " Hari")
                    # Normalisasi casing (Opsional tapi bagus untuk konsistensi)
                    t = t.replace("/Month", "/Bulan").replace("/Year", "/Tahun")
                    return t
                return "-"
        except:
            pass
        return "-"

    # ------------------------------------------------------------------
    def _dedup_list(self, items):
        seen = set()
        result = []
        for item in items:
            key = item.strip().lower()
            if key and key not in seen:
                seen.add(key)
                result.append(item.strip())
        return result

    # ------------------------------------------------------------------
    def _extract_p_from_container(self, container_locator, excluded_labels):
        """
        Ambil teks dari semua elemen <p> di dalam container.

        Struktur tag item Glints (skills & benefits):
            <div class="TagStyle...">
              <span class="TagContentStyle...">
                <div class="TagContentWrapper...">
                  <p class="TypographyStyles / Skillssc__TagName">TEKS DI SINI</p>
                </div>
              </span>
            </div>

        Selector langsung ke <p> menghindari double-read dari parent element.
        """
        items = []
        try:
            if container_locator.count() == 0:
                return []
            p_els = container_locator.first.locator("p")
            for i in range(p_els.count()):
                t = p_els.nth(i).inner_text().strip()
                if t and t.lower() not in excluded_labels:
                    items.append(t)
        except:
            pass
        return self._dedup_list(items)

    # ------------------------------------------------------------------
    def scrape_keyword(self, keyword, page=1):
        query = keyword.replace(" ", "%20")
        url = (
            f"https://glints.com/id/opportunities/jobs/explore"
            f"?keyword={query}&country=ID&locationName=Indonesia"
        )
        url = (
            f"https://glints.com/id/opportunities/jobs/explore"
            f"?keyword={query}&country=ID&locationName=Indonesia"
        )
        # Jangan tambahkan &page= di URL karena Glints server memblokirnya untuk guest
            
        data_ekstrak = []

        print(f"\n [Glints] Scraping keyword: {keyword.upper()} (Page: {page})")

        try:
            # =========================================================
            # FASE 1: Kumpulkan semua link job dari halaman search
            # =========================================================
            print(" [Fase 1] Membuka halaman pencarian Glints...")
            self.page.goto(url, wait_until="domcontentloaded")
            time.sleep(random.uniform(3.0, 5.0))

            # Upaya Bypass Login Wall / Popup Modal (Pertama kali)
            try:
                self.page.keyboard.press("Escape")
                time.sleep(1)
                
                # Hapus elemen login nudge (Glints hard wall)
                self.page.evaluate('''
                    // Hapus banner login yang menutupi jobs
                    const nudge = document.getElementById('see-more-jobs-login-nudge');
                    if(nudge) nudge.remove();
                    
                    const overlay = document.querySelector('[class*="LoginNudgeViewsc__Overlay"]');
                    if(overlay) overlay.remove();
                    
                    const blurredContainer = document.querySelector('[class*="LoginNudgeViewsc__BlurredJobCardListContainer"]');
                    if(blurredContainer) {
                        blurredContainer.style.filter = 'none';
                        blurredContainer.style.opacity = '1';
                    }
                    
                    // Hapus pop-up modal login & signup
                    const popup = document.getElementById('login-signup-popup');
                    if(popup) {
                        let parent = popup.parentElement;
                        while(parent && parent.tagName !== 'BODY') {
                            if(window.getComputedStyle(parent).position === 'fixed') {
                                parent.remove();
                                break;
                            }
                            parent = parent.parentElement;
                        }
                        if (document.body.contains(popup)) popup.remove();
                    }
                    
                    // Kembalikan kemampuan scroll halaman
                    document.body.style.overflow = 'auto';
                    document.documentElement.style.overflow = 'auto';
                    
                    // Hapus efek blur jika ada class yang menggunakan blur
                    const blurredElements = document.querySelectorAll('*');
                    for (let el of blurredElements) {
                        const style = window.getComputedStyle(el);
                        if (style.filter.includes('blur')) {
                            el.style.filter = 'none';
                        }
                    }
                ''')
                time.sleep(1)
            except:
                pass

            # Fungsi pembantu untuk membunuh dinding login yang mungkin muncul tiba-tiba saat scroll
            def kill_login_wall():
                try:
                    self.page.evaluate('''
                        const nudge = document.getElementById('see-more-jobs-login-nudge');
                        if(nudge) nudge.remove();
                        const overlay = document.querySelector('[class*="LoginNudgeViewsc__Overlay"]');
                        if(overlay) overlay.remove();
                        const blurredContainer = document.querySelector('[class*="LoginNudgeViewsc__BlurredJobCardListContainer"]');
                        if(blurredContainer) {
                            blurredContainer.style.filter = 'none';
                            blurredContainer.style.opacity = '1';
                        }
                        const popup = document.getElementById('login-signup-popup');
                        if(popup) {
                            let parent = popup.parentElement;
                            while(parent && parent.tagName !== 'BODY') {
                                if(window.getComputedStyle(parent).position === 'fixed') { parent.remove(); break; }
                                parent = parent.parentElement;
                            }
                            if (document.body.contains(popup)) popup.remove();
                        }
                        document.body.style.overflow = 'auto';
                        document.documentElement.style.overflow = 'auto';
                        const blurredElements = document.querySelectorAll('*');
                        for (let el of blurredElements) {
                            const style = window.getComputedStyle(el);
                            if (style.filter.includes('blur')) el.style.filter = 'none';
                        }
                    ''')
                except:
                    pass

            kill_login_wall()

            try:
                self.page.wait_for_selector(
                    "a[href*='/id/opportunities/jobs/']",
                    state="attached",
                    timeout=20000
                )
            except:
                print(f" [Fase 1] Kartu job tidak muncul. URL: {self.page.url}")
                try:
                    self.page.screenshot(path="debug_glints_list.png")
                except:
                    pass
                return []

            # Infinite Scroll Logic untuk mendapatkan data pekerjaan halaman ke-N
            target_items = page * 30
            max_scroll_attempts = page * 10
            
            print(f" [Fase 1] Melakukan infinite scroll untuk mencapai ~{target_items} pekerjaan (Target Halaman {page})...")
            
            for _ in range(max_scroll_attempts):
                self.page.mouse.wheel(0, 1500)
                time.sleep(1.2)
                kill_login_wall() # Terus hancurkan wall jika muncul
                
                # Cek jumlah pekerjaan yang sudah termuat di DOM
                current_count = self.page.locator("a[href*='/id/opportunities/jobs/']").count()
                if current_count >= target_items:
                    break

            link_elems = self.page.locator("a[href*='/id/opportunities/jobs/']")
            total = link_elems.count()

            job_links = []
            seen = set()
            for i in range(total):
                href = link_elems.nth(i).get_attribute("href")
                if href and "/explore" not in href:
                    clean_href = re.sub(r'\?.*$', '', href)
                    if clean_href in seen:
                        continue
                    if re.search(r"/jobs/[^/]+/[0-9a-f\-]{8,}", clean_href):
                        full_url = ("https://glints.com" + clean_href) if clean_href.startswith("/") else clean_href
                        seen.add(clean_href)
                        job_links.append(full_url)

            # Hanya ambil potongan (slice) pekerjaan untuk 'page' ini (misal page 2: index 30 sampai 60)
            start_idx = (page - 1) * 30
            end_idx = page * 30
            job_links = job_links[start_idx:end_idx]
            
            print(f" [Fase 1] Berhasil kumpulkan {len(job_links)} job unik untuk Halaman {page}.")

            if not job_links:
                print(" [Fase 1] Tidak ada link job ditemukan.")
                return []

            # =========================================================
            # FASE 2: Buka tiap halaman detail dan ekstrak semua data
            # =========================================================
            print(" [Fase 2] Mulai buka halaman detail setiap job...")

            for idx, job_url in enumerate(job_links):
                print(f"  [{idx+1}/{len(job_links)}] {job_url.split('/')[-1][:50]}...")

                judul           = "-"
                perusahaan      = "-"
                lokasi          = "-"
                gaji            = "-"
                jenis_pekerjaan = "-"
                deskripsi       = "-"
                kualifikasi     = "-"
                skills          = "-"
                benefits        = "-"
                persyaratan_tag = "-"
                kategori_utama  = "-"
                sub_kategori    = "-"

                try:
                    self.page.goto(job_url, wait_until="domcontentloaded")
                    time.sleep(random.uniform(2.0, 3.5))

                    try:
                        self.page.wait_for_selector("h1, [class*='JobTitle']", timeout=15000)
                    except:
                        print(f"      [Skip] Halaman tidak termuat: {job_url}")
                        continue

                    # --- Judul ---
                    judul = self._teks_bersih(self.page.locator("[class*='JobTitle']"))
                    if judul == "-":
                        judul = self._teks_bersih(self.page.locator("h1"))

                    # --- Perusahaan ---
                    perusahaan = self._teks_bersih(self.page.locator("[class*='CompanyName']").first)

                    # --- Lokasi ---
                    # Struktur HTML:
                    #   <div class="AboutCompanySectionsc__AddressHeader...">Alamat kantor</div>
                    #   <p class="TypographyStyles...">Jalan Tubagus Ismail VII No. 21, ...</p>
                    # Selector CSS "+ p" artinya ambil <p> yang langsung mengikuti div tersebut
                    alamat_loc = self.page.locator(
                        "[class*='AboutCompanySectionsc__AddressHeader'] + p"
                    )
                    if alamat_loc.count() > 0:
                        lokasi = alamat_loc.first.inner_text().strip() or "-"

                    # --- Gaji & Bonus ---
                    # Glints memisahkan gaji pokok dan bonus dalam class yang berbeda
                    basic_salary_loc = self.page.locator("[class*='BasicSalary']")
                    bonus_salary_loc = self.page.locator("[class*='BonusSalary']")
                    
                    basic_salary = self._teks_bersih(basic_salary_loc)
                    bonus_salary = self._teks_bersih(bonus_salary_loc)
                    
                    if basic_salary != "-" and "tidak menampilkan" not in basic_salary.lower():
                        gaji = basic_salary
                    else:
                        # Fallback ke selector umum jika class spesifik tidak ditemukan
                        gaji_raw = self._teks_bersih(self.page.locator("[class*='Salary']"))
                        if gaji_raw != "-" and "tidak menampilkan" not in gaji_raw.lower():
                            gaji = gaji_raw
                            
                    if bonus_salary != "-" and "tidak menampilkan" not in bonus_salary.lower():
                        # Hapus kata "Bonus" di awal jika ada (agar tidak "+ Bonus: Bonus")
                        clean_bonus = re.sub(r'^bonus\s*:?\s*', '', bonus_salary, flags=re.IGNORECASE).strip()
                        # Ganti month menjadi Bulan
                        clean_bonus = clean_bonus.replace("/month", "/Bulan").replace("month", "Bulan")
                        benefits_bonus = clean_bonus if clean_bonus else "-"
                    else:
                        benefits_bonus = "-"

                    # --- Kategori Utama & Sub Kategori ---
                    # Glints menyimpan kategori dalam link dengan href /id/job-category/...
                    # Kategori utama: /id/job-category/SLUG          (1 segmen setelah prefix)
                    # Sub kategori:   /id/job-category/SLUG/SLUG/... (lebih dari 1 segmen)
                    # Meskipun class HTML sama, dibedakan lewat panjang path di href.
                    # CATATAN: URL Glints pakai tanda hubung (-), BUKAN underscore (_).
                    kategori_links = self.page.locator("a[href*='/id/job-category/']")
                    for i in range(kategori_links.count()):
                        try:
                            href_kat = kategori_links.nth(i).get_attribute("href") or ""
                            # Normalisasi: hapus query string, ambil path saja
                            path_kat = href_kat.split("?")[0].rstrip("/")
                            # Potong prefix /id/job-category/ untuk hitung segmen
                            prefix = "/id/job-category/"
                            if prefix in path_kat:
                                after_prefix = path_kat.split(prefix, 1)[1]
                                segmen = [s for s in after_prefix.split("/") if s]
                                teks_kat = kategori_links.nth(i).inner_text().strip()
                                if not teks_kat:
                                    continue
                                if len(segmen) == 1:
                                    # Satu segmen = kategori utama
                                    kategori_utama = teks_kat
                                elif len(segmen) > 1:
                                    # Lebih dari satu segmen = sub kategori
                                    sub_kategori = teks_kat
                        except:
                            pass

                    # --- Jenis Pekerjaan ---
                    html_penuh = self.page.content()
                    match_jp = re.search(
                        r'(Full-time|Part-time|Penuh Waktu|Paruh Waktu|Kontrak|Magang|Freelance|Tetap)',
                        html_penuh, re.IGNORECASE
                    )
                    if match_jp:
                        jenis_pekerjaan = match_jp.group(1)

                    # --- Skills ---
                    # Container: Opportunitysc__SkillsContainer
                    # Teks ada di <p class="Skillssc__TagName...">
                    skills_container = self.page.locator("[class*='SkillsContainer']")
                    skill_list = self._extract_p_from_container(
                        skills_container,
                        excluded_labels={"skills", "skill"}
                    )
                    skills = " | ".join(skill_list) if skill_list else "-"

                    # --- Benefits ---
                    # Container: Opportunitysc__BenefitsContainer
                    # Teks ada di <p class="TypographyStyles..."> dalam Benefitssc__TagOverride
                    benefits_container = self.page.locator("[class*='BenefitsContainer']")
                    benefit_list = self._extract_p_from_container(
                        benefits_container,
                        excluded_labels={"benefit kerja", "benefit", "benefits"}
                    )
                    benefits = " | ".join(benefit_list) if benefit_list else "-"

                    # --- Persyaratan Kerja ---
                    # Struktur HTML:
                    #   <div class="JobRequirementssc__TagsWrapper...">
                    #     <div class="TagStyle... JobRequirementssc__Tag...">
                    #       <span class="TagContentStyle...">
                    #         <div class="TagContentWrapper...">Remote/Dari rumah</div>
                    #       </span>
                    #     </div>
                    #   </div>
                    # Teks ada langsung di <div class="TagContentWrapper"> (bukan di <p>)
                    req_wrappers = self.page.locator(
                        "[class*='JobRequirementssc__TagsWrapper'] [class*='TagContentWrapper']"
                    )
                    if req_wrappers.count() > 0:
                        req_list = []
                        for i in range(req_wrappers.count()):
                            t = req_wrappers.nth(i).inner_text().strip()
                            if t:
                                req_list.append(t)
                        persyaratan_tag = " | ".join(self._dedup_list(req_list)) or "-"

                    # --- Deskripsi & Kualifikasi ---
                    desc_loc = self.page.locator("[class*='DescriptionContainer']")
                    if desc_loc.count() > 0:
                        html_desc = desc_loc.first.inner_html()
                        html_desc = re.sub(
                            r'<(br|p|li|div|h[1-6]|/p|/li|/div|/h[1-6])[^>]*>',
                            '\n', html_desc, flags=re.IGNORECASE
                        )
                        teks = re.sub(r'<[^>]+>', '', html_desc)
                        teks = html_module.unescape(teks)
                        teks = re.sub(r'[ \t]+', ' ', teks)
                        teks = re.sub(r'\n\s*\n+', '\n', teks).strip()

                        baris_teks        = teks.split('\n')
                        deskripsi_lines   = []
                        kualifikasi_lines = []
                        state = "deskripsi"

                        kw_kualifikasi = ["qualification", "kualifikasi", "requirement", "persyaratan", "syarat", "ideally have", "what you need", "keterampilan", "who you are"]
                        kw_company     = ["about us", "tentang kami", "company description", "tentang perusahaan", "who we are"]
                        kw_jobdesc     = ["job description", "deskripsi pekerjaan", "tanggung jawab", "responsibilit", "what you will do", "day-to-day", "the role", "tugas", "tentang pekerjaan", "about the job"]

                        for line in baris_teks:
                            line_clean = line.strip()
                            if not line_clean:
                                continue
                            line_lower = line_clean.lower()

                            if len(line_lower) < 70:
                                test = re.sub(r'[^a-z0-9 ]', '', line_lower)
                                if any(kw in test for kw in kw_company):
                                    state = "company"; continue
                                elif any(kw in test for kw in kw_kualifikasi):
                                    state = "kualifikasi"; continue
                                elif any(kw in test for kw in kw_jobdesc):
                                    state = "deskripsi"; continue

                            if state == "kualifikasi":
                                c = line_clean.lstrip('•-*▪❖✓"\'').strip()
                                if c: kualifikasi_lines.append(c)
                            elif state == "deskripsi":
                                c = line_clean.lstrip('•-*▪❖✓"\'').strip()
                                if c: deskripsi_lines.append(c)

                        deskripsi   = "\n".join(deskripsi_lines).strip() or "-"
                        kualifikasi = " | ".join(kualifikasi_lines).strip() or "-"

                    # Jika kualifikasi tidak ditemukan dari parsing deskripsi,
                    # gunakan data dari tag Persyaratan Kerja sebagai fallback
                    if kualifikasi == "-" and persyaratan_tag != "-":
                        kualifikasi = persyaratan_tag

                except Exception as e:
                    print(f"      [Error] {e}")

                data_ekstrak.append({
                    "Judul_Pekerjaan":         judul,
                    "Jenis_Pekerjaan":         jenis_pekerjaan,
                    "Nama_Perusahaan":         perusahaan,
                    "Lokasi":                  lokasi,
                    "Rentang_Gaji":            gaji,
                    "Bonus":                   benefits_bonus,
                    "Kategori_Utama":          kategori_utama,
                    "Sub_Kategori":            sub_kategori,
                    "Skills":                  skills,
                    "Benefit_Pekerjaan":       benefits,
                    "Kualifikasi_Persyaratan": kualifikasi,
                    "Deskripsi_Pekerjaan":     deskripsi,
                    "Link_Lowongan":           job_url,
                })
                print(f"    [TERSIMPAN] {judul[:50]}")

                if idx < len(job_links) - 1:
                    time.sleep(random.uniform(1.5, 3.0))

        except Exception as e:
            print(f"  Terjadi kesalahan kritikal: {e}")

        return data_ekstrak

    # ------------------------------------------------------------------
    def close(self):
        print(" Menutup Browser Playwright...")
        try:
            self.context.close()
            self.browser.close()
            self.playwright.stop()
        except:
            pass