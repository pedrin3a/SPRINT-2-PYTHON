
# =========================================================
# JOVI CAMERA ULTRA
# =========================================================

import sys
import cv2
import time
import os

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QAction,
    QMenu,
    QFrame,
    QGraphicsDropShadowEffect
)

from PyQt5.QtGui import (
    QImage,
    QPixmap,
    QColor
)

from PyQt5.QtCore import (
    Qt,
    QTimer
)

# =========================================================
# PASTA MIDIAS
# =========================================================
os.makedirs("midias", exist_ok=True)


# =========================================================
# CLASSE
# =========================================================
class JoviCamera(QWidget):

    def __init__(self):
        super().__init__()

        # =================================================
        # JANELA
        # =================================================
        self.setWindowTitle("JOVI Camera Ultra")

        self.setFixedSize(430, 850)

        self.setStyleSheet("""
            QWidget{
                background-color: #050505;
                color: white;
                font-family: Segoe UI;
            }
        """)

        # =================================================
        # VARIÁVEIS
        # =================================================
        self.current_mode = "Foto"

        self.is_recording = False

        self.video_writer = None

        self.smile_capture_enabled = False

        self.last_smile_capture = 0

        # =================================================
        # IA
        # =================================================
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_smile.xml"
        )

        # =================================================
        # CAMERA
        # =================================================
        self.cap = cv2.VideoCapture(0)

        # =================================================
        # LAYOUT PRINCIPAL
        # =================================================
        self.main_layout = QVBoxLayout()

        self.main_layout.setContentsMargins(
            15,
            15,
            15,
            15
        )

        self.main_layout.setSpacing(12)

        # =================================================
        # TOPO
        # =================================================
        self.top_bar = QHBoxLayout()

        self.flash_btn = QPushButton("⚡")

        self.settings_btn = QPushButton("⚙")

        for btn in [
            self.flash_btn,
            self.settings_btn
        ]:

            btn.setFixedSize(50, 50)

            btn.setStyleSheet("""
                QPushButton{
                    background-color: rgba(255,255,255,0.06);
                    border-radius: 25px;
                    color: white;
                    font-size: 22px;
                    border: 1px solid rgba(255,255,255,0.1);
                }

                QPushButton:hover{
                    background-color: rgba(255,255,255,0.15);
                }
            """)

        self.top_bar.addWidget(self.flash_btn)

        self.top_bar.addStretch()

        self.top_bar.addWidget(self.settings_btn)

        self.main_layout.addLayout(
            self.top_bar
        )

        # =================================================
        # CAMERA FRAME
        # =================================================
        self.camera_frame = QFrame()

        self.camera_frame.setFixedSize(
            390,
            620
        )

        self.camera_frame.setStyleSheet("""
            QFrame{
                background-color: #111;
                border-radius: 35px;
                border: 2px solid #1f1f1f;
            }
        """)

        shadow = QGraphicsDropShadowEffect()

        shadow.setBlurRadius(30)

        shadow.setColor(
            QColor(0, 0, 0, 180)
        )

        shadow.setOffset(0, 10)

        self.camera_frame.setGraphicsEffect(
            shadow
        )

        self.camera_layout = QVBoxLayout()

        self.camera_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # =================================================
        # CAMERA LABEL
        # =================================================
        self.camera_label = QLabel()

        self.camera_label.setFixedSize(
            390,
            620
        )

        self.camera_label.setAlignment(
            Qt.AlignCenter
        )

        self.camera_label.setStyleSheet("""
            QLabel{
                border-radius: 35px;
                background-color: black;
            }
        """)

        # =================================================
        # ediçao de documento
        # =================================================
        self.document_editor = QTextEdit()

        self.document_editor.hide()

        self.document_editor.setFixedSize(
            390,
            620
        )

        self.document_editor.setPlaceholderText(
            "Digite algo..."
        )

        self.document_editor.setStyleSheet("""
            QTextEdit{
                background-color: white;
                color: black;
                border-radius: 35px;
                padding: 25px;
                font-size: 18px;
                border: none;
            }
        """)

        self.camera_layout.addWidget(
            self.camera_label
        )

        self.camera_layout.addWidget(
            self.document_editor
        )

        self.camera_frame.setLayout(
            self.camera_layout
        )

        self.main_layout.addWidget(
            self.camera_frame,
            alignment=Qt.AlignCenter
        )

        # =================================================
        # MODOS
        # =================================================
        self.modes_layout = QHBoxLayout()

        self.modes_layout.setSpacing(10)

        self.video_mode = QPushButton("Vídeo")

        self.photo_mode = QPushButton("Foto")

        self.portrait_mode = QPushButton("Retrato")

        self.night_mode = QPushButton("Night")

        self.document_mode = QPushButton("Documento")

        self.summary_mode_btn = QPushButton(
            "Resumo IA"
        )

        self.mode_buttons = [
            self.video_mode,
            self.photo_mode,
            self.portrait_mode,
            self.night_mode,
            self.document_mode,
            self.summary_mode_btn
        ]

        for btn in self.mode_buttons:

            btn.setFixedSize(95, 42)

            btn.setStyleSheet("""
                QPushButton{
                    background-color: #111;
                    border-radius: 18px;
                    color: #999;
                    font-size: 12px;
                    font-weight: bold;
                    border: 1px solid #222;
                }

                QPushButton:hover{
                    background-color: #1c1c1c;
                    color: white;
                }
            """)

            self.modes_layout.addWidget(btn)

        self.main_layout.addLayout(
            self.modes_layout
        )

        # =================================================
        # BOTÃO CAPTURA
        # =================================================
        self.capture_layout = QHBoxLayout()

        self.capture_btn = QPushButton()

        self.capture_btn.setFixedSize(
            90,
            90
        )

        self.capture_btn.setStyleSheet("""
            QPushButton{
                background-color: white;
                border-radius: 45px;
                border: 6px solid #666;
            }

            QPushButton:hover{
                background-color: #ddd;
            }
        """)

        capture_shadow = QGraphicsDropShadowEffect()

        capture_shadow.setBlurRadius(25)

        capture_shadow.setColor(
            QColor(255, 255, 255, 70)
        )

        capture_shadow.setOffset(0, 0)

        self.capture_btn.setGraphicsEffect(
            capture_shadow
        )

        self.capture_layout.addStretch()

        self.capture_layout.addWidget(
            self.capture_btn
        )

        self.capture_layout.addStretch()

        self.main_layout.addSpacing(10)

        self.main_layout.addLayout(
            self.capture_layout
        )

        self.setLayout(
            self.main_layout
        )

        # =================================================
        # MENU CONFIG
        # =================================================
        self.menu = QMenu()

        self.menu.setStyleSheet("""
            QMenu{
                background-color: #111;
                border-radius: 18px;
                border: 1px solid #222;
                color: white;
                padding: 10px;
            }

            QMenu::item{
                padding: 12px 25px;
                border-radius: 10px;
            }

            QMenu::item:selected{
                background-color: #222;
            }
        """)

        # REMOVE SETINHA DO MENU
        self.settings_btn.clicked.connect(
            lambda: self.menu.exec_(
                self.settings_btn.mapToGlobal(
                    self.settings_btn.rect().bottomLeft()
                )
            )
        )

        # =================================================
        # ACTIONS
        # =================================================
        self.night_action = QAction(
            "Night",
            self,
            checkable=True,
            checked=True
        )

        self.portrait_action = QAction(
            "Retrato",
            self,
            checkable=True,
            checked=True
        )

        self.document_action = QAction(
            "Documento",
            self,
            checkable=True,
            checked=True
        )

        self.summary_action = QAction(
            "Resumo IA",
            self,
            checkable=True,
            checked=True
        )

        self.smile_action = QAction(
            "Foto ao sorrir (IA)",
            self,
            checkable=True
        )

        self.menu.addAction(
            self.night_action
        )

        self.menu.addAction(
            self.portrait_action
        )

        self.menu.addAction(
            self.document_action
        )

        self.menu.addAction(
            self.summary_action
        )

        self.menu.addSeparator()

        self.menu.addAction(
            self.smile_action
        )

        # =================================================
        # CONEXÕES
        # =================================================
        self.video_mode.clicked.connect(
            lambda: self.change_mode("Vídeo")
        )

        self.photo_mode.clicked.connect(
            lambda: self.change_mode("Foto")
        )

        self.portrait_mode.clicked.connect(
            lambda: self.change_mode("Retrato")
        )

        self.night_mode.clicked.connect(
            lambda: self.change_mode("Night")
        )

        self.document_mode.clicked.connect(
            lambda: self.change_mode("Documento")
        )

        self.summary_mode_btn.clicked.connect(
            lambda: self.change_mode("Resumo IA")
        )

        self.capture_btn.clicked.connect(
            self.capture_action
        )

        self.smile_action.triggered.connect(
            self.toggle_smile_ai
        )

        self.night_action.triggered.connect(
            self.update_modes_visibility
        )

        self.portrait_action.triggered.connect(
            self.update_modes_visibility
        )

        self.document_action.triggered.connect(
            self.update_modes_visibility
        )

        self.summary_action.triggered.connect(
            self.update_modes_visibility
        )

        # =================================================
        # TIMER
        # =================================================
        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_frame
        )

        self.timer.start(30)

        self.highlight_selected_mode()

    # =====================================================
    # MODOS VISIBILIDADE
    # =====================================================
    def update_modes_visibility(self):

        self.night_mode.setVisible(
            self.night_action.isChecked()
        )

        self.portrait_mode.setVisible(
            self.portrait_action.isChecked()
        )

        self.document_mode.setVisible(
            self.document_action.isChecked()
        )

        self.summary_mode_btn.setVisible(
            self.summary_action.isChecked()
        )

    # =====================================================
    # BOTÃO SELECIONADO
    # =====================================================
    def highlight_selected_mode(self):

        mapping = {
            "Vídeo": self.video_mode,
            "Foto": self.photo_mode,
            "Retrato": self.portrait_mode,
            "Night": self.night_mode,
            "Documento": self.document_mode,
            "Resumo IA": self.summary_mode_btn
        }

        for btn in self.mode_buttons:

            btn.setStyleSheet("""
                QPushButton{
                    background-color: #111;
                    border-radius: 18px;
                    color: #999;
                    font-size: 12px;
                    font-weight: bold;
                    border: 1px solid #222;
                }

                QPushButton:hover{
                    background-color: #1c1c1c;
                    color: white;
                }
            """)

        selected = mapping.get(
            self.current_mode
        )

        if selected:

            selected.setStyleSheet("""
                QPushButton{
                    background-color: white;
                    border-radius: 18px;
                    color: black;
                    font-size: 12px;
                    font-weight: bold;
                    border: none;
                }
            """)

    # =====================================================
    # TROCAR MODO
    # =====================================================
    def change_mode(self, mode):

        self.current_mode = mode

        if mode in [
            "Documento",
            "Resumo IA"
        ]:

            self.camera_label.hide()

            self.document_editor.show()

        else:

            self.document_editor.hide()

            self.camera_label.show()

        self.highlight_selected_mode()

    # =====================================================
    # IA SORRISO
    # =====================================================
    def toggle_smile_ai(self):

        self.smile_capture_enabled = (
            self.smile_action.isChecked()
        )

    # =====================================================
    # RESUMO IA
    # =====================================================
    def summarize_text(self):

        text = (
            self.document_editor
            .toPlainText()
        )

        if len(text.strip()) < 20:

            self.document_editor.setText(
                "Digite um texto maior."
            )

            return

        self.document_editor.setText(
            "Resumindo..."
        )

        QApplication.processEvents()

        time.sleep(1)

        sentences = text.split(".")

        summary = ""

        for sentence in sentences[:2]:

            summary += (
                sentence.strip() + ". "
            )

        self.document_editor.setText(
            summary
        )

    # =====================================================
    # FRAME CAMERA
    # =====================================================
    def update_frame(self):

        if self.current_mode in [
            "Documento",
            "Resumo IA"
        ]:
            return

        ret, frame = self.cap.read()

        if ret:

            self.current_frame = frame.copy()

            if self.smile_capture_enabled:

                gray = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY
                )

                faces = (
                    self.face_cascade
                    .detectMultiScale(
                        gray,
                        1.3,
                        5
                    )
                )

                for (
                    x,
                    y,
                    w,
                    h
                ) in faces:

                    roi_gray = gray[
                        y:y+h,
                        x:x+w
                    ]

                    smiles = (
                        self.smile_cascade
                        .detectMultiScale(
                            roi_gray,
                            1.7,
                            20
                        )
                    )

                    if len(smiles) > 0:

                        current_time = time.time()

                        if (
                            current_time -
                            self.last_smile_capture
                            > 3
                        ):

                            self.capture_photo()

                            self.last_smile_capture = (
                                current_time
                            )

            if (
                self.is_recording and
                self.video_writer
            ):

                self.video_writer.write(frame)

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            h, w, ch = rgb.shape

            bytes_per_line = ch * w

            qt_image = QImage(
                rgb.data,
                w,
                h,
                bytes_per_line,
                QImage.Format_RGB888
            )

            pixmap = QPixmap.fromImage(
                qt_image
            )

            scaled = pixmap.scaled(
                self.camera_label.width(),
                self.camera_label.height(),
                Qt.KeepAspectRatioByExpanding
            )

            self.camera_label.setPixmap(
                scaled
            )

    # =====================================================
    # FOTO IA
    # =====================================================
    def capture_photo(self):

        filename = (
            f"midias/sorriso_"
            f"{int(time.time())}.jpg"
        )

        cv2.imwrite(
            filename,
            self.current_frame
        )

    # =====================================================
    # CAPTURA
    # =====================================================
    def capture_action(self):

        if self.current_mode == "Resumo IA":

            self.summarize_text()

            return

        if self.current_mode == "Documento":

            text = (
                self.document_editor
                .toPlainText()
            )

            filename = (
                f"midias/documento_"
                f"{int(time.time())}.txt"
            )

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(text)

            return

        if self.current_mode in [
            "Foto",
            "Night",
            "Retrato"
        ]:

            filename = (
                f"midias/foto_"
                f"{int(time.time())}.jpg"
            )

            cv2.imwrite(
                filename,
                self.current_frame
            )

        elif self.current_mode == "Vídeo":

            if not self.is_recording:

                filename = (
                    f"midias/video_"
                    f"{int(time.time())}.avi"
                )

                fourcc = (
                    cv2.VideoWriter_fourcc(
                        *'XVID'
                    )
                )

                self.video_writer = (
                    cv2.VideoWriter(
                        filename,
                        fourcc,
                        20.0,
                        (
                            self.current_frame.shape[1],
                            self.current_frame.shape[0]
                        )
                    )
                )

                self.is_recording = True

                self.capture_btn.setStyleSheet("""
                    QPushButton{
                        background-color: red;
                        border-radius: 45px;
                        border: 6px solid white;
                    }
                """)

            else:

                self.is_recording = False

                self.video_writer.release()

                self.capture_btn.setStyleSheet("""
                    QPushButton{
                        background-color: white;
                        border-radius: 45px;
                        border: 6px solid #666;
                    }
                """)

    # =====================================================
    # FECHAR
    # =====================================================
    def closeEvent(self, event):

        if self.video_writer:
            self.video_writer.release()

        self.cap.release()

        event.accept()


# =========================================================
# EXECUTAR
# =========================================================
app = QApplication(sys.argv)

window = JoviCamera()

window.show()

sys.exit(app.exec_())