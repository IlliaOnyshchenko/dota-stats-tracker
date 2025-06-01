import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QScrollArea, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont, QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt
import requests


class APIManager:
    @staticmethod
    def get_player_stats(player_id):
        url = f"https://api.opendota.com/api/players/{player_id}"
        response = requests.get(url)
        data = response.json()
        return data

    @staticmethod
    def get_match_history(player_id):
        url = f"https://api.opendota.com/api/players/{player_id}/matches"
        response = requests.get(url)
        data = response.json()
        return data

    @staticmethod
    def get_hero_name(hero_id):
        url = f"https://api.opendota.com/api/heroes"
        response = requests.get(url)
        data = response.json()
        for hero in data:
            if hero["id"] == hero_id:
                return hero["localized_name"]
        return None

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.sort_order = Qt.DescendingOrder
        self.last_sorted_column = None

    def init_ui(self):
        self.setWindowTitle("Dota 2 Stats")
        layout = QVBoxLayout()

        # Styling
        self.set_background_color("#333333")
        font = QFont()
        font.setPointSize(18)

        # Player ID input
        player_id_label = QLabel("Steam ID:", self)
        player_id_label.setStyleSheet("color: white;")
        player_id_label.setFont(font)
        layout.addWidget(player_id_label)

        self.player_id_input = QLineEdit(self)
        self.player_id_input.setStyleSheet("background-color: lightgrey;")
        self.player_id_input.setPlaceholderText("Enter Steam ID")
        layout.addWidget(self.player_id_input)

        # Player stats button
        search_button = QPushButton("Search Player Stats", self)
        search_button.setStyleSheet("background-color: darkgray; color: white; padding: 10px; border-radius: 5px; font-size: 16px;")
        search_button.clicked.connect(self.on_search_clicked)
        layout.addWidget(search_button)

        # Player stats section
        player_stats_group = QGroupBox("Player Stats")
        player_stats_group.setStyleSheet("color: darkgray; font-size: 20px;")
        player_stats_layout = QVBoxLayout()

        player_info_layout = QHBoxLayout()
        self.avatar_label = QLabel(self)
        self.avatar_label.setMaximumSize(128, 128)
        player_info_layout.setAlignment(Qt.AlignTop)  # Add alignment flag
        player_info_layout.addWidget(self.avatar_label)

        self.player_stats_label = QLabel(self)
        self.player_stats_label.setStyleSheet("color: darkgray; font-weight: bold;")
        player_info_layout.addWidget(self.player_stats_label)

        player_stats_layout.addLayout(player_info_layout)
        player_stats_group.setLayout(player_stats_layout)

        # Match history section
        match_history_group = QGroupBox("Match History")
        match_history_group.setStyleSheet("color: darkgray; font-size: 20px;")
        match_history_layout = QVBoxLayout()

        self.match_history_table = QTableWidget()
        self.match_history_table.setColumnCount(4)
        self.match_history_table.setHorizontalHeaderLabels(["Match ID", "Hero", "Duration", "Result"])
        self.match_history_table.horizontalHeader().setStretchLastSection(True)
        self.match_history_table.setStyleSheet("color: lightgrey; background-color: #222222;")  # Set background color of the table

        # Set text color of the table
        palette = self.match_history_table.palette()
        palette.setColor(QPalette.Text, Qt.white)
        self.match_history_table.setPalette(palette)

        self.match_history_table.horizontalHeader().sectionClicked.connect(
            self.sort_table)  # Connect the sort_table method to header sectionClicked signal

        match_history_layout.addWidget(self.match_history_table)

        match_history_group.setLayout(match_history_layout)

        # Scroll area for player stats and match history sections
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget(scroll_area)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.addWidget(player_stats_group)
        scroll_layout.addWidget(match_history_group)
        scroll_content.setLayout(scroll_layout)

        scroll_area.setWidget(scroll_content)

        layout.addWidget(scroll_area)

        self.setLayout(layout)
        self.setGeometry(1000, 1000, 1000, 1000)
        self.show()

    def set_background_color(self, color):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

    def on_search_clicked(self):
        player_id = self.player_id_input.text()
        player_stats = APIManager.get_player_stats(player_id)

        if "profile" in player_stats:
            player_stats_text = ""

            # Avatar and nickname
            if "profile" in player_stats and "avatarfull" in player_stats["profile"]:
                avatar_url = player_stats["profile"]["avatarfull"]
                pixmap = QPixmap()
                pixmap.loadFromData(requests.get(avatar_url).content)
                self.avatar_label.setPixmap(pixmap.scaledToWidth(128, Qt.TransformationMode.SmoothTransformation))

            if "profile" in player_stats and "personaname" in player_stats["profile"]:
                player_stats_text += f"<strong>Nickname:</strong> {player_stats['profile']['personaname']}<br>"

            if "profile" in player_stats and "last_login" in player_stats["profile"]:
                last_login = player_stats["profile"]["last_login"]
                player_stats_text += f"<strong>Last Login:</strong> {last_login}<br>"

            if "competitive_rank" in player_stats:
                competitive_rank = player_stats["competitive_rank"]
                player_stats_text += f"<strong>Competitive Rank:</strong> {competitive_rank}<br>"

            if "rank_tier" in player_stats:
                rank_tier = player_stats["rank_tier"]
                player_stats_text += f"<strong>Rank Tier:</strong> {rank_tier}<br>"

            if "mmr_estimate" in player_stats and "estimate" in player_stats["mmr_estimate"]:
                mmr_estimate = player_stats["mmr_estimate"]["estimate"]
                player_stats_text += f"<strong>Rating:</strong> {mmr_estimate}<br>"

            self.player_stats_label.setText(player_stats_text)
            self.player_stats_label.setStyleSheet("color: lightgrey;")

            # Get match history
            match_history = APIManager.get_match_history(player_id)
            match_history_text = "<strong></strong><br>"

            if isinstance(match_history, list):
                last_20_matches = match_history[:20]  # Get the last 20 matches

                self.match_history_table.setRowCount(len(last_20_matches))

                for i, match in enumerate(last_20_matches):
                    match_id = match["match_id"]
                    hero_id = match["hero_id"]
                    hero_name = APIManager.get_hero_name(hero_id)
                    duration = match["duration"]
                    radiant_win = match["radiant_win"]
                    result = "Win" if radiant_win else "Loss"

                    match_id_item = QTableWidgetItem(str(match_id))
                    hero_name_item = QTableWidgetItem(hero_name)
                    duration_item = QTableWidgetItem(f"{duration // 60}:{duration % 60:02d}")
                    result_item = QTableWidgetItem(result)

                    match_id_item.setFlags(match_id_item.flags() & ~Qt.ItemIsEditable)
                    hero_name_item.setFlags(hero_name_item.flags() & ~Qt.ItemIsEditable)
                    duration_item.setFlags(duration_item.flags() & ~Qt.ItemIsEditable)
                    result_item.setFlags(result_item.flags() & ~Qt.ItemIsEditable)

                    self.match_history_table.setItem(i, 0, match_id_item)
                    self.match_history_table.setItem(i, 1, hero_name_item)
                    self.match_history_table.setItem(i, 2, duration_item)
                    self.match_history_table.setItem(i, 3, result_item)
        else:
            QMessageBox.critical(self, "Error", "Invalid player ID.")

    def sort_table(self, logical_index):
        if logical_index == 1:  # Сортувати лише за стовпцем з назвами героїв (індекс 1)
            if self.last_sorted_column == logical_index:
                self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
            else:
                self.last_sorted_column = logical_index
                self.sort_order = Qt.AscendingOrder

            self.match_history_table.sortItems(logical_index, self.sort_order)
        else:
            if self.last_sorted_column == logical_index:
                self.sort_order = Qt.AscendingOrder if self.sort_order == Qt.DescendingOrder else Qt.DescendingOrder
            else:
                self.last_sorted_column = logical_index
                self.sort_order = Qt.DescendingOrder

            self.match_history_table.sortItems(logical_index, self.sort_order)

        # Add sort markers
        header = self.match_history_table.horizontalHeader()
        header.setSortIndicator(logical_index, self.sort_order)
        header.setSortIndicatorShown(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    sys.exit(app.exec_())