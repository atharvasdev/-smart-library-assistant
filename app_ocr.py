import re
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytesseract
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Library Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path(__file__).with_name("library.db")

SAMPLE_BOOKS = [
    ("Operating System Concepts", "Abraham Silberschatz", "Computer Science", 2),
    ("Database System Concepts", "Abraham Silberschatz", "Computer Science", 2),
    ("Introduction to Algorithms", "Thomas H. Cormen", "Computer Science", 2),
    ("Computer Networks", "Andrew S. Tanenbaum", "Computer Science", 2),
    ("Engineering Mathematics", "B. S. Grewal", "Mathematics", 3),
    ("Basic Electrical Engineering", "D. P. Kothari", "Electrical", 1),
    ("Engineering Physics", "G. Vijayakumari", "Physics", 4),
    ("Python Programming", "Reema Thareja", "Programming", 2),
    ("Let Us C", "Yashavant Kanetkar", "Programming", 2),
    ("Clean Code", "Robert C. Martin", "Programming", 2),
    (
        "Discrete Mathematics and Its Applications",
        "Kenneth H. Rosen",
        "Mathematics",
        3,
    ),
    ("Concepts of Physics", "H. C. Verma", "Physics", 4),
]

BIN_NAMES = {
    1: "Electrical",
    2: "Computer Science / Programming",
    3: "Mathematics",
    4: "Physics",
}

BIN_EMOJI = {
    1: "🔴",
    2: "🟢",
    3: "🔵",
    4: "🟡",
}


# --------------------------------------------------
# THEME
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap'
    );

    :root {
        --espresso: #2B1D16;
        --walnut: #513628;
        --gold: #C9A45C;
        --amber: #E5A23B;
        --cream: #F7F1E5;
        --paper: #FFFFFF;
        --ink: #35251D;
        --muted: #806F62;
        --border: #E8DDCC;
        --green: #477553;
    }

    .stApp {
        background-color: var(--cream);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(247, 241, 229, 0.95);
    }

    [data-testid="stSidebar"] {
        background: var(--espresso);
        border-right: 1px solid #624832;
    }

    [data-testid="stSidebar"] * {
        color: #F7F1E5;
    }

    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: var(--amber);
    }

    [data-testid="stSidebar"] hr {
        border-color: #624832;
    }

    h1, h2, h3 {
        color: var(--espresso) !important;
        font-family: 'Playfair Display', Georgia, serif !important;
    }

    p, label, .stCaption {
        color: var(--ink);
    }

    .brand-label {
        color: var(--gold);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero {
        background: linear-gradient(
            125deg,
            #2B1D16 0%,
            #513628 72%,
            #765438 100%
        );
        padding: 36px 38px;
        border-radius: 20px;
        margin: 12px 0 28px 0;
        border: 1px solid #73563A;
        box-shadow: 0 12px 32px rgba(43, 29, 22, 0.12);
    }

    .hero h1 {
        color: #FFF8EA !important;
        font-size: 2.35rem !important;
        margin-bottom: 10px;
    }

    .hero p {
        color: #E6D6BE !important;
        font-size: 1rem;
        margin-bottom: 0;
        line-height: 1.7;
    }

    .hero-tag {
        display: inline-block;
        background: rgba(229, 162, 59, 0.15);
        color: #F0C875;
        border: 1px solid rgba(229, 162, 59, 0.4);
        padding: 6px 12px;
        border-radius: 30px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }

    .section-label {
        color: #9A7440;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .info-card {
        background: var(--paper);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 21px;
        min-height: 125px;
        box-shadow: 0 4px 15px rgba(43, 29, 22, 0.035);
    }

    .info-card .label {
        color: var(--muted);
        font-size: 0.83rem;
        margin-bottom: 10px;
    }

    .info-card .value {
        color: var(--espresso);
        font-size: 1.8rem;
        font-weight: 700;
    }

    .info-card .note {
        color: #9A7440;
        font-size: 0.76rem;
        margin-top: 6px;
    }

    .result-card {
        background: #FFFCF6;
        border: 1px solid var(--gold);
        border-left: 5px solid var(--amber);
        border-radius: 15px;
        padding: 24px;
        margin: 12px 0;
    }

    .result-bin {
        color: #9A6720;
        font-size: 2rem;
        font-weight: 800;
    }

    .result-title {
        color: var(--espresso);
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.45rem;
        margin: 8px 0;
    }

    .muted-text {
        color: var(--muted);
        font-size: 0.9rem;
    }

    div.stButton > button[kind="primary"] {
        background: var(--amber);
        color: var(--espresso);
        border: 1px solid var(--amber);
        border-radius: 9px;
        font-weight: 700;
        min-height: 45px;
    }

    div.stButton > button[kind="primary"]:hover {
        background: var(--gold);
        border-color: var(--gold);
        color: var(--espresso);
    }

    div.stButton > button {
        border-radius: 9px;
    }

    div[data-testid="stMetric"] {
        background: var(--paper);
        border: 1px solid var(--border);
        padding: 16px;
        border-radius: 13px;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    div[data-testid="stMetricValue"] {
        color: var(--espresso);
    }

    div[data-testid="stFileUploader"] {
        background: #FFFCF6;
        border: 1px dashed var(--gold);
        border-radius: 12px;
        padding: 12px;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        color: var(--walnut);
        font-weight: 600;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #9A6720;
        border-bottom-color: var(--amber);
    }

    .footer {
        border-top: 1px solid var(--border);
        margin-top: 38px;
        padding-top: 18px;
        color: var(--muted);
        font-size: 0.8rem;
        text-align: center;
    }

    @media (max-width: 700px) {
        .hero {
            padding: 25px 22px;
        }

        .hero h1 {
            font-size: 1.8rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with connect() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT NOT NULL,
                bin_number INTEGER NOT NULL
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scanned_at TEXT NOT NULL,
                query TEXT NOT NULL,
                matched_title TEXT,
                status TEXT NOT NULL,
                bin_number INTEGER
            )
            """
        )

        if con.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
            con.executemany(
                """
                INSERT INTO books(title, author, category, bin_number)
                VALUES (?, ?, ?, ?)
                """,
                SAMPLE_BOOKS,
            )

        con.commit()


def load_books():
    with connect() as con:
        return pd.read_sql_query(
            """
            SELECT id, title, author, category, bin_number
            FROM books
            ORDER BY title
            """,
            con,
        )


def load_history(limit=100):
    with connect() as con:
        return pd.read_sql_query(
            """
            SELECT
                scanned_at AS 'Time',
                query AS 'Search text / OCR text',
                matched_title AS 'Matched book',
                status AS 'Status',
                bin_number AS 'Bin'
            FROM scans
            ORDER BY id DESC
            LIMIT ?
            """,
            con,
            params=(limit,),
        )


# --------------------------------------------------
# BOOK IDENTIFICATION
# --------------------------------------------------

def normalize(text):
    return " ".join(re.findall(r"[a-z0-9]+", str(text).lower()))


def match_book(query, books):
    q = normalize(query)

    if not q:
        return None

    titles = books["title"].fillna("").astype(str)
    normalized_titles = titles.apply(normalize)

    exact = books[normalized_titles == q]

    if not exact.empty:
        return exact.iloc[0]

    contained = books[
        normalized_titles.apply(lambda title: bool(title) and title in q)
    ]

    if not contained.empty:
        longest_index = normalized_titles.loc[contained.index].str.len().idxmax()
        return books.loc[longest_index]

    reverse = books[
        normalized_titles.apply(
            lambda title: bool(q) and q in title and len(q) >= 8
        )
    ]

    if not reverse.empty:
        shortest_index = normalized_titles.loc[reverse.index].str.len().idxmin()
        return books.loc[shortest_index]

    query_tokens = {token for token in q.split() if len(token) >= 4}
    best_index = None
    best_score = 0

    for index, row in books.iterrows():
        title_tokens = set(normalize(row["title"]).split())
        score = len(query_tokens & title_tokens)

        if score > best_score:
            best_index = index
            best_score = score

    if best_index is not None and best_score >= 2:
        return books.loc[best_index]

    return None


def record_scan(query, result, status=None):
    if status is None:
        status = "Recognized" if result is not None else "Not found"

    with connect() as con:
        con.execute(
            """
            INSERT INTO scans(
                scanned_at, query, matched_title, status, bin_number
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(query)[:2000],
                str(result["title"]) if result is not None else "",
                status,
                int(result["bin_number"]) if result is not None else None,
            ),
        )
        con.commit()


def extract_text(image):
    image = ImageOps.exif_transpose(image).convert("RGB")

    width, height = image.size

    if max(width, height) < 1400:
        scale = 1400 / max(width, height)
        image = image.resize((int(width * scale), int(height * scale)))

    gray = ImageOps.grayscale(image)
    gray = ImageEnhance.Contrast(gray).enhance(1.7)

    return pytesseract.image_to_string(
        gray,
        config="--psm 6",
    ).strip()


# --------------------------------------------------
# DISPLAY HELPERS
# --------------------------------------------------

def show_result(result):
    if result is None:
        st.error("We couldn't confidently identify this book.")

        st.info(
            "Try a clearer image or search for the title manually. "
            "The book must exist in the catalogue to be matched."
        )
        return

    bin_number = int(result["bin_number"])
    bin_name = BIN_NAMES.get(bin_number, "General Collection")

    st.markdown(
        f"""
        <div class="result-card">
            <div class="section-label">BOOK IDENTIFIED</div>
            <div class="result-title">{result['title']}</div>
            <p class="muted-text">by {result['author']}</p>
            <hr style="border-color:#E8DDCC">
            <p><strong>Category:</strong> {result['category']}</p>
            <p><strong>Storage location:</strong> {bin_name}</p>
            <div class="result-bin">BIN {bin_number}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success(f"Place this book in Bin {bin_number}.")

    st.caption(
        "The bin assignment is provided by the software. "
        "Physical LED control is not yet connected."
    )


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="info-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# APPLICATION INITIALIZATION
# --------------------------------------------------

init_db()
books = load_books()
history = load_history()

total_books = len(books)
total_categories = books["category"].nunique()
total_bins = books["bin_number"].nunique()
total_scans = len(history)

recognized_count = int((history["Status"] == "Recognized").sum())

with st.sidebar:
    st.markdown(
        """
        <div style="padding:10px 0 22px 0">
            <div style="font-size:2.2rem">📚</div>
            <div style="
                color:#E5A23B;
                font-size:1.05rem;
                font-weight:800;
                letter-spacing:1px;
            ">SMART LIBRARY</div>
            <div style="color:#D6C3AA;font-size:0.8rem">
                Intelligent Book Organization
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Scan a Book",
            "Book Collection",
            "Categories & Bins",
            "Scan History",
            "About Project",
        ],
        label_visibility="visible",
    )

    st.divider()

    st.markdown("**STORAGE MAP**")

    for number, name in BIN_NAMES.items():
        st.write(f"{BIN_EMOJI[number]} Bin {number} — {name}")

    st.divider()

    st.caption("SOFTWARE STATUS")
    st.success("Application running")

    st.caption(
        "Hardware status: Not connected"
    )


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

if page == "Overview":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-tag">SMART LIBRARY · SOFTWARE MVP</div>
            <h1>A smarter way to organize books.</h1>
            <p>
                Identify books, retrieve their categories, and discover
                their assigned storage bins from one simple dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">LIBRARY AT A GLANCE</div>',
                unsafe_allow_html=True)

    st.markdown("## Your library overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("BOOKS IN CATALOGUE", total_books, "Stored book records")

    with c2:
        metric_card("CATEGORIES", total_categories, "Distinct categories")

    with c3:
        metric_card("STORAGE BINS", total_bins, "Configured bin numbers")

    with c4:
        metric_card("RECENT SCANS", total_scans, "Latest 100 scan records")

    st.write("")

    left, right = st.columns([1.35, 1])

    with left:
        st.markdown("### Recent book records")

        if books.empty:
            st.info("Your catalogue is empty.")
        else:
            st.dataframe(
                books[["title", "author", "category", "bin_number"]].head(5),
                width="stretch",
                hide_index=True,
            )

    with right:
        st.markdown("### Start here")

        st.markdown(
            """
            **Scan a book**

            Upload a cover image and identify its catalogue record.

            **Browse the collection**

            Search books and check their categories.

            **Find a storage bin**

            View the configured category-to-bin assignments.
            """
        )

        if st.button("Open book scanner", type="primary", width="stretch"):
            st.session_state["navigation_page"] = "Scan a Book"
            st.rerun()

    st.markdown(
        '<div class="footer">SMART LIBRARY ASSISTANT · SCAN. IDENTIFY. ORGANIZE.</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# SCAN A BOOK
# --------------------------------------------------

elif page == "Scan a Book":
    st.markdown('<div class="section-label">BOOK RECOGNITION</div>',
                unsafe_allow_html=True)

    st.title("Scan a book")
    st.write(
        "Upload a clear book-cover image or use your camera. "
        "The application will extract text and search the catalogue."
    )

    scan_method = st.radio(
        "Choose image source",
        ["Upload image", "Use camera"],
        horizontal=True,
    )

    if scan_method == "Upload image":
        image_file = st.file_uploader(
            "Choose a book-cover image",
            type=["png", "jpg", "jpeg", "webp"],
            key="book_cover_upload",
        )
    else:
        image_file = st.camera_input(
            "Take a photo of the book cover",
            key="book_cover_camera",
        )

    if image_file is not None:
        image = None

        try:
            image = Image.open(image_file)

            left, right = st.columns([1, 1])

            with left:
                st.image(
                    image,
                    caption="Image selected for scanning",
                    width="stretch",
                )

            with right:
                st.markdown("### Ready to identify?")
                st.write(
                    "For the best results, keep the book title clear, "
                    "well-lit, and facing the camera."
                )

                if st.button(
                    "Read cover and find bin",
                    type="primary",
                    width="stretch",
                ):
                    with st.spinner("Extracting text and searching catalogue..."):
                        try:
                            extracted_text = extract_text(image)
                        except Exception as exc:
                            extracted_text = ""
                            st.error(f"OCR error: {exc}")

                    st.session_state["ocr_text"] = extracted_text
                    st.session_state["ocr_image_ready"] = True

                    if extracted_text:
                        result = match_book(extracted_text, books)
                        record_scan(extracted_text, result)

                        st.session_state["last_result"] = (
                            result.to_dict() if result is not None else None
                        )
                        st.session_state["last_query"] = extracted_text
                        st.session_state["last_scan_source"] = "Image OCR"
                    else:
                        record_scan(
                            "[OCR returned no text]",
                            None,
                            status="No text detected",
                        )

                        st.session_state["last_result"] = None
                        st.session_state["last_query"] = ""
                        st.session_state["last_scan_source"] = "Image OCR"

                    st.rerun()

        except Exception as exc:
            st.error(f"Could not open the image: {exc}")

    if st.session_state.get("ocr_image_ready"):
        with st.expander("View extracted OCR text"):
            st.text_area(
                "Text extracted from the image",
                value=st.session_state.get("ocr_text", ""),
                height=130,
                disabled=True,
            )

    st.divider()

    st.markdown("### Or search by title")

    with st.form("manual_search_form"):
        query = st.text_input(
            "Book title",
            placeholder="e.g. Operating System Concepts",
        )

        submitted = st.form_submit_button(
            "Find book",
            type="primary",
        )

    if submitted:
        result = match_book(query, books)
        record_scan(query, result)

        st.session_state["last_result"] = (
            result.to_dict() if result is not None else None
        )
        st.session_state["last_query"] = query
        st.session_state["last_scan_source"] = "Manual search"

    if "last_result" in st.session_state:
        st.divider()
        st.markdown("### Identification result")
        show_result(st.session_state["last_result"])


# --------------------------------------------------
# BOOK COLLECTION
# --------------------------------------------------

elif page == "Book Collection":
    st.markdown('<div class="section-label">LIBRARY CATALOGUE</div>',
                unsafe_allow_html=True)

    st.title("Book collection")
    st.write("Browse and search the books stored in the catalogue.")

    filt = st.text_input(
        "Search by title, author, or category",
        placeholder="Start typing...",
    )

    view = books.copy()

    if filt:
        mask = (
            view["title"].str.contains(filt, case=False, na=False, regex=False)
            | view["author"].str.contains(filt, case=False, na=False, regex=False)
            | view["category"].str.contains(filt, case=False, na=False, regex=False)
        )

        view = view[mask]

    st.caption(f"{len(view)} book records found")

    st.dataframe(
        view.drop(columns=["id"]),
        width="stretch",
        hide_index=True,
    )

    with st.expander("Add a book to the catalogue"):
        with st.form("add_book_form", clear_on_submit=True):
            title = st.text_input("Title")
            author = st.text_input("Author")

            category = st.selectbox(
                "Category",
                [
                    "Computer Science",
                    "Programming",
                    "Mathematics",
                    "Electrical",
                    "Physics",
                    "Other",
                ],
            )

            bin_number = st.selectbox(
                "Bin number",
                [1, 2, 3, 4],
            )

            submitted = st.form_submit_button("Add book")

            if submitted:
                if not title.strip() or not author.strip():
                    st.error("Enter both the title and author.")
                else:
                    with connect() as con:
                        con.execute(
                            """
                            INSERT INTO books(title, author, category, bin_number)
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                title.strip(),
                                author.strip(),
                                category,
                                bin_number,
                            ),
                        )
                        con.commit()

                    st.success("Book added successfully.")
                    st.rerun()


# --------------------------------------------------
# CATEGORIES AND BINS
# --------------------------------------------------

elif page == "Categories & Bins":
    st.markdown('<div class="section-label">STORAGE ORGANIZATION</div>',
                unsafe_allow_html=True)

    st.title("Categories & bins")
    st.write(
        "Explore the current category and storage-bin assignments."
    )

    if not books.empty:
        summary = (
            books.groupby(["bin_number", "category"])
            .size()
            .reset_index(name="Books")
            .sort_values(["bin_number", "category"])
        )

        for bin_number in sorted(books["bin_number"].unique()):
            bin_number = int(bin_number)
            bin_books = books[books["bin_number"] == bin_number]

            st.markdown(
                f"### {BIN_EMOJI.get(bin_number, '📦')} "
                f"Bin {bin_number} — {BIN_NAMES.get(bin_number, 'General Collection')}"
            )

            st.caption(
                f"{len(bin_books)} catalogue records assigned to this bin"
            )

            st.dataframe(
                bin_books[["title", "author", "category"]],
                width="stretch",
                hide_index=True,
            )

            st.write("")

        st.markdown("### Category summary")

        st.dataframe(
            summary,
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("Add books to populate the storage map.")


# --------------------------------------------------
# SCAN HISTORY
# --------------------------------------------------

elif page == "Scan History":
    st.markdown('<div class="section-label">ACTIVITY RECORDS</div>',
                unsafe_allow_html=True)

    st.title("Scan history")
    st.write("Review previous searches and book-identification attempts.")

    history = load_history()

    if history.empty:
        st.info("No scans have been recorded yet.")
    else:
        recognized = int((history["Status"] == "Recognized").sum())
        unsuccessful = len(history) - recognized

        c1, c2, c3 = st.columns(3)

        c1.metric("Scans shown", len(history))
        c2.metric("Recognized", recognized)
        c3.metric("Other outcomes", unsuccessful)

        st.dataframe(
            history,
            width="stretch",
            hide_index=True,
        )

        st.download_button(
            "Download history as CSV",
            history.to_csv(index=False).encode("utf-8"),
            "scan_history.csv",
            "text/csv",
        )


# --------------------------------------------------
# ABOUT PROJECT
# --------------------------------------------------

elif page == "About Project":
    st.markdown('<div class="section-label">PROJECT INFORMATION</div>',
                unsafe_allow_html=True)

    st.title("About Smart Library Assistant")

    st.markdown(
        """
        ### Our objective

        Reduce manual effort in book identification and storage-bin
        assignment through OCR, catalogue matching, and a simple dashboard.

        ### How the system works

        1. Upload or capture a book-cover image.
        2. Tesseract OCR extracts visible text.
        3. The application matches the text against the local catalogue.
        4. The stored category and bin assignment are displayed.
        5. The scan attempt is recorded in the local database.
        6. The librarian places the book in the indicated bin.

        ### Current implementation

        - Streamlit dashboard
        - SQLite book catalogue
        - Image upload and camera capture
        - OCR-based text extraction
        - Catalogue matching
        - Category and bin retrieval
        - Scan history and CSV export

        ### Current limitations

        - The catalogue contains sample data.
        - Recognition depends on image quality and title matching.
        - Unknown books require catalogue entry or manual handling.
        - Physical LED control is not integrated yet.
        - The application does not physically move books.
        """
    )

    st.info(
        "The current application is a software MVP. "
        "Hardware integration is planned as the next development stage."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        SMART LIBRARY ASSISTANT · SCAN. IDENTIFY. ORGANIZE.
        <br>
        OCR-assisted book identification and storage guidance
    </div>
    """,
    unsafe_allow_html=True,
)