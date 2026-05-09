
# renders Algo control grid page
@app.route("/admin_home", methods=["GET"])
def admin_home():

    ########################################################
    # 🔹 ENSURE ACTIVE ALGO IN SESSION
    ########################################################

    if "algo_selection" not in session:
        session["algo_selection"] = "Alpha"

    algo_name = session["algo_selection"]

    ########################################################
    # 🔹 FLASH / UPDATE FLAGS (temporary only)
    ########################################################

    algo_updated = session.pop("algo_updated", False)
    run_status_updated = session.pop("run_status_updated", None)
    schedule_updated = session.pop("schedule_updated", False)
    trade_window_updated = session.pop("trade_window_updated", False)
    scraper_inputs_updated = session.pop("scraper_inputs_updated", False)  # ✅ keep flag
    demo_user = session.pop("demo_user", False)




    ########################################################
    # 🔹 LOAD RUN STATUS
    ########################################################

    status_df = run_sql("""
        SELECT status
        FROM admin__algo_status
        WHERE algo_name = %s
    """, (algo_name,)).to_df()

    if not status_df.empty:
        algo_status = status_df["status"].iloc[0]
        algo_running = (algo_status == "on")
    else:
        algo_status = "off"
        algo_running = False
















    ########################################################
    # 🔹 SESSION DATA FOR TEMPLATE
    ########################################################

    session_data = {
        "corporate_name": "HoodAlgo.com",
        "algo_name": algo_name
    }

    ########################################################
    # 🔹 RENDER
    ########################################################

    return render_template(
        "buttons.html",
        page_name="Admin",

        session_data=session_data,
        algo_name=algo_name,
        algo_selection=algo_name,
        algo_status=algo_status,
        algo_running=algo_running,

        algo_updated=algo_updated,
        run_status_updated=run_status_updated,
        schedule_updated=schedule_updated,
        trade_window_updated=trade_window_updated,
        scraper_inputs_updated=scraper_inputs_updated,  # ✅ keep flash flag
        demo_user=demo_user,

    )




@app.route("/handle_trade_window", methods=["POST"])
def handle_trade_window():

    algo_name = session.get("algo_selection")

    start_time = request.form.get("trade_start_time")
    end_time = request.form.get("trade_end_time")

    run_sql(f"""
        INSERT INTO admin__algo__trade_window
        (algo_name, start_time, end_time)
        VALUES
        ('{algo_name}', '{start_time}', '{end_time}')
        ON DUPLICATE KEY UPDATE
            start_time = VALUES(start_time),
            end_time = VALUES(end_time),
            updated_at = NOW()
    """)

    session["trade_window_updated"] = True

    return redirect("/admin_home")






@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("index", tab="login", msg="Signed out"))








@app.route("/handle_scraper_inputs", methods=["POST"])
def handle_scraper_inputs():

    ############################################################
    # 1️⃣ Algo from Session
    ############################################################

    algo = session["algo_selection"]


    ############################################################
    # 2️⃣ Convert Checkboxes → 0 / 1
    ############################################################

    scraper_stocktwits   = 1 if request.form.get("scraper_stocktwits") else 0
    scraper_wsj          = 1 if request.form.get("scraper_wsj") else 0
    scraper_tradingview  = 1 if request.form.get("scraper_tradingview") else 0
    scraper_benzinga     = 1 if request.form.get("scraper_benzinga") else 0
    scraper_yahoo        = 1 if request.form.get("scraper_yahoo") else 0
    scraper_etf_universe = 1 if request.form.get("scraper_etf_universe") else 0


    ############################################################
    # 3️⃣ UPSERT
    ############################################################

    run_sql(f"""
        INSERT INTO admin__Algo__scraper_inputs (
            algo,
            scraper_stocktwits,
            scraper_wsj,
            scraper_tradingview,
            scraper_benzinga,
            scraper_yahoo,
            scraper_etf_universe
        )
        VALUES (
            '{algo}',
            {scraper_stocktwits},
            {scraper_wsj},
            {scraper_tradingview},
            {scraper_benzinga},
            {scraper_yahoo},
            {scraper_etf_universe}
        )
        ON DUPLICATE KEY UPDATE
            scraper_stocktwits   = VALUES(scraper_stocktwits),
            scraper_wsj          = VALUES(scraper_wsj),
            scraper_tradingview  = VALUES(scraper_tradingview),
            scraper_benzinga     = VALUES(scraper_benzinga),
            scraper_yahoo        = VALUES(scraper_yahoo),
            scraper_etf_universe = VALUES(scraper_etf_universe);
    """)


    session['scraper_inputs_updated'] = True

    return redirect(request.referrer)











#chooses which algo you have selcted 
@app.route("/handle_algo_selection", methods=["POST"])
def handle_algo_selection():

    selected_algo = request.form.get("algo_selection")
    current_algo = session.get("algo_selection")

    if selected_algo != current_algo:
        session["algo_selection"] = selected_algo
        session["algo_updated"] = True

    return redirect(url_for("admin_home"))






@app.route("/algo_run_status", methods=["POST"])
def algo_run_status():

    run_status = request.form.get("run_status")
    algo_name  = session.get("algo_selection", "Alpha")

    if run_status not in ["on", "off", "test"]:
        return redirect(url_for("admin_home"))

    run_sql("""
        UPDATE admin__algo_status
        SET status = %s
        WHERE algo_name = %s
    """, (run_status, algo_name))

    session["run_status_updated"] = run_status

    return redirect(url_for("admin_home"))











@app.route("/handle_run_schedule", methods=["POST"])
def handle_run_schedule():

    algo_name = session.get("algo_selection")

    if not algo_name:
        return redirect("/")

    run_forever = 1 if request.form.get("run_forever") else 0
    run_selected_days = 1 if request.form.get("run_selected_days") else 0

    start_date = request.form.get("start_date") or None
    end_date = request.form.get("end_date") or None

    if run_forever == 1:
        run_selected_days = 0
        start_date = None
        end_date = None

    if run_selected_days == 1:
        if not start_date or not end_date:
            run_selected_days = 0
            start_date = None
            end_date = None

    run_sql(f"""
        INSERT INTO admin__algo__schedule
        (
            algo_name,
            run_forever,
            run_selected_days,
            start_date,
            end_date
        )
        VALUES
        (
            '{algo_name}',
            {run_forever},
            {run_selected_days},
            { 'NULL' if not start_date else f"'{start_date}'" },
            { 'NULL' if not end_date else f"'{end_date}'" }
        )
        ON DUPLICATE KEY UPDATE
            run_forever = VALUES(run_forever),
            run_selected_days = VALUES(run_selected_days),
            start_date = VALUES(start_date),
            end_date = VALUES(end_date),
            updated_at = NOW()
    """)

    session["schedule_updated"] = True

    return redirect("/admin_home")


