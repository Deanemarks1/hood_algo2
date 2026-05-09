




@app.route("/", methods=["GET"])
def index():

    email_sent = session.pop("email_sent", None)




    # ==========================================================
    # BASE SCREENSHOT DIR
    # ==========================================================
    base_ss_dir = base_dir + "static/front_end/screen_shots/"

    # ==========================================================
    # HELPER (INLINE, SIMPLE)
    # ==========================================================
    def load_images(subdir):
        folder = base_ss_dir + subdir
        if not os.path.exists(folder):
            return []

        files = [
            f for f in os.listdir(folder)
            if f.lower().endswith(".png")
        ]
        files.sort()
        return [f"/static/front_end/screen_shots/{subdir}/{f}" for f in files]

    # ==========================================================
    # MAIN IMAGE STRIP (TOP)
    # ==========================================================
    image_list = []
    if os.path.exists(base_ss_dir):
        files = [
            f for f in os.listdir(base_ss_dir)
            if f.lower().endswith(".png")
        ]
        files.sort()
        image_list = [f"/static/front_end/screen_shots/{f}" for f in files]

    # ==========================================================
    # ROW IMAGE LISTS (ALWAYS DEFINED)
    # ==========================================================
    row_1_image_list = load_images("row_1")
    row_2_image_list = load_images("row_2")
    row_3_image_list = load_images("row_3")








    account_created = session.pop("account_created", False)
    cancel_after_str = session.pop("cancel_after_str", False)
    

    account_deleted = session.pop("account_deleted", False)



    email = session.pop("email", False)
    password = session.pop("password", False)







    return render_template(
        "index.html",
        email_sent=email_sent,
        row_1_image_list=row_1_image_list,
        row_2_image_list = row_2_image_list,
        row_3_image_list = row_3_image_list, 
        STRIPE_FRONT_END_KEY = STRIPE_FRONT_END_KEY, 


        account_created = account_created,
        cancel_after_str = cancel_after_str, 
        email = email, 
        password = password, 
        account_deleted = account_deleted


    )










@app.route("/about")
def about():
    return('build_me')















@app.route("/login", methods=["POST"])
@app.route("/handle_operator_sign_in", methods=["POST"])
def handle_operator_sign_in():
    try:

        # ==================================================
        # 1️⃣ INPUT VALIDATION
        # ==================================================
        if True:
            email = (request.form.get("email") or "").strip().lower()
            password = (request.form.get("password") or "").strip()

            if not email or not password:
                return jsonify({
                    "success": False,
                    "error": "Enter email & password"
                }), 400


        # ==================================================
        # 🔐 ADMIN OVERRIDE
        # ==================================================
        if True:
            if email == "deanemarks1@gmail.com" and password == "1234":
                return jsonify({
                    "success": True,
                    "redirect": url_for("admin_home")
                })


        # ==================================================
        # 2️⃣ AUTHENTICATE USER
        # ==================================================
        if True:
            user_df = run_sql("""
                SELECT *
                FROM admin_profiles
                WHERE LOWER(email) = %s
                  AND password = %s
                LIMIT 1
            """, params=(email, password)).df

            if user_df.empty:
                return jsonify({
                    "success": False,
                    "error": "No account found"
                }), 400

            session_data = user_df.to_dict(orient="records")[0]
            session_data["user_id"] = int(session_data["user_id"])


        # ==================================================
        # 3️⃣ EVENT CONTEXT RESOLUTION
        # ==================================================
        if True:
            events_df = run_sql("""
                SELECT *
                FROM events
                WHERE user_id = %s
                ORDER BY event_id DESC
                LIMIT 1
            """, params=(session_data["user_id"],)).df

            # ----------------------------------------------
            # No events yet → send to create flow
            # ----------------------------------------------
            if events_df.empty:

                session["session_data"] = session_data
                session["is_admin"] = False

                return jsonify({
                    "success": True,
                    "redirect": url_for("create_initial_event")
                })


            # ----------------------------------------------
            # Select active event
            # ----------------------------------------------
            event = events_df.iloc[0]
            session_data["event_id"] = int(event["event_id"])
            session_data["event_name"] = str(event["event_name"])


        # ==================================================
        # 4️⃣ SESSION + RESPONSE
        # ==================================================
        if True:
            session["session_data"] = session_data
            session["demo_repeat_checker"] = True
            session["is_admin"] = False

            print(f"✅ LOGIN SUCCESS: {email} | Event: {session_data['event_name']}")

            return jsonify({
                "success": True,
                "redirect": url_for("user_home")
            })


    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500













@app.route("/launch_demo", methods=["POST"])
def launch_demo():
    try:

        # ==================================================
        # 1️⃣ INPUT VALIDATION
        # ==================================================
        if True:
            email = 'deanemarks1@gmail.com'
            password = '1234'

            if not email or not password:
                return jsonify({
                    "success": False,
                    "error": "Enter email & password"
                }), 400


        # ==================================================
        # 🔐 ADMIN OVERRIDE
        # ==================================================
        if True:
            if email == "deanemarks1@gmail.com" and password == "1234":
                session['demo_user'] = True
                return redirect(url_for("admin_home"))


        # ==================================================
        # 2️⃣ AUTHENTICATE USER
        # ==================================================
        if True:
            user_df = run_sql("""
                SELECT *
                FROM admin_profiles
                WHERE LOWER(email) = %s
                  AND password = %s
                LIMIT 1
            """, params=(email, password)).df

            if user_df.empty:
                return jsonify({
                    "success": False,
                    "error": "No account found"
                }), 400

            session_data = user_df.to_dict(orient="records")[0]
            session_data["user_id"] = int(session_data["user_id"])


        # ==================================================
        # 3️⃣ EVENT CONTEXT RESOLUTION
        # ==================================================
        if True:
            events_df = run_sql("""
                SELECT *
                FROM events
                WHERE user_id = %s
                ORDER BY event_id DESC
                LIMIT 1
            """, params=(session_data["user_id"],)).df

            # ----------------------------------------------
            # No events yet → send to create flow
            # ----------------------------------------------
            if events_df.empty:

                session["session_data"] = session_data
                session["is_admin"] = False

                return jsonify({
                    "success": True,
                    "redirect": url_for("create_initial_event")
                })


            # ----------------------------------------------
            # Select active event
            # ----------------------------------------------
            event = events_df.iloc[0]
            session_data["event_id"] = int(event["event_id"])
            session_data["event_name"] = str(event["event_name"])


        # ==================================================
        # 4️⃣ SESSION + RESPONSE
        # ==================================================
        if True:
            session["session_data"] = session_data
            session["demo_repeat_checker"] = True
            session["is_admin"] = False

            print(f"✅ LOGIN SUCCESS: {email} | Event: {session_data['event_name']}")

            return jsonify({
                "success": True,
                "redirect": url_for("user_home")
            })


    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500



