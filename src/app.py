from dotenv import load_dotenv

from ui.styles import apply_page_config_and_styles
from ui.sidebar import render_sidebar
from ui.chat import render_chat_area
from core.utils import init_session_state


def main():
    load_dotenv()
    apply_page_config_and_styles()

    # Initialize session state (moved here for clarity)
    init_session_state()
    # Render UI
    render_sidebar()
    render_chat_area()


if __name__ == "__main__":
    import os
    os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
    main()
