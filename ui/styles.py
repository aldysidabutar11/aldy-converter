from .theme import Colors, Typography, Radius

def build_stylesheet():
    return f"""
        * {{
            font-family: {Typography.FAMILY};
            color: {Colors.TEXT_PRIMARY};
        }}
        
        QMainWindow {{
            background-color: {Colors.BASE_BG};
        }}
        
        /* Secondary Buttons (Clear All) - Outline darker */
        QPushButton {{
            background-color: transparent;
            border: 1px solid {Colors.TEXT_PRIMARY};
            border-radius: {Radius.SMALL};
            color: {Colors.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: 500;
            padding: 8px 32px;
        }}
        QPushButton:hover {{
            background-color: rgba(0, 0, 0, 0.05);
        }}
        
        /* Progress Bar */
        QProgressBar {{
            background-color: #EEEEEE;
            border: none;
            border-radius: 2px;
            height: 4px;
            text-align: center;
            color: transparent;
        }}
        QProgressBar::chunk {{
            background-color: #A5D6A7;
            border-radius: 2px;
        }}
        
        /* QMessageBox */
        QMessageBox {{
            background-color: {Colors.BASE_BG};
            border: 1px solid {Colors.BORDER_MAIN};
            border-radius: {Radius.MEDIUM};
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 8px;
        }}
        QScrollBar::handle:vertical {{
            background: #D29A94;
            min-height: 20px;
            border-radius: 4px;
        }}
    """
