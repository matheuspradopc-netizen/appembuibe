"""
Serviço de Geração de PDF - Expresso Embuibe
Gera PDFs das passagens usando ReportLab
"""
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
import base64
from datetime import datetime
from decimal import Decimal
from ..config import settings


class PDFService:
    """Serviço para geração de PDFs de passagens"""

    def __init__(self):
        self.page_width, self.page_height = A6
        self.margin = 10 * mm

    def gerar_passagem_pdf(
        self,
        numero: int,
        cliente_nome: str,
        cidade: str,
        local_embarque: str,
        data_viagem: str,
        horario: str,
        valor: Decimal,
        forma_pagamento: str,
        data_emissao: datetime,
        atendente_nome: str
    ) -> str:
        """
        Gera o PDF de uma passagem

        Args:
            numero: Número da passagem
            cliente_nome: Nome do passageiro
            cidade: Cidade de origem
            local_embarque: Local de embarque
            data_viagem: Data da viagem (formatada)
            horario: Horário da viagem (formatado)
            valor: Valor da passagem
            forma_pagamento: Forma de pagamento
            data_emissao: Data/hora de emissão
            atendente_nome: Nome do atendente

        Returns:
            PDF em base64
        """
        # Cria buffer em memória
        buffer = BytesIO()

        # Cria o canvas
        c = canvas.Canvas(buffer, pagesize=A6)

        # Posição Y inicial
        y = self.page_height - self.margin

        # CABEÇALHO
        y = self._desenhar_cabecalho(c, y)

        # NÚMERO DA PASSAGEM
        y = self._desenhar_numero_passagem(c, y, numero)

        # DADOS DA PASSAGEM
        y = self._desenhar_campo(c, y, "Passageiro:", cliente_nome)
        y = self._desenhar_campo(c, y, "Origem:", f"{cidade} - {local_embarque}")
        y = self._desenhar_campo(c, y, "Destino:", settings.DESTINO_PADRAO)
        y = self._desenhar_campo(c, y, "Data da Viagem:", data_viagem)
        y = self._desenhar_campo(c, y, "Horário:", horario)
        y = self._desenhar_campo(c, y, "Valor:", f"R$ {valor:.2f}")
        y = self._desenhar_campo(c, y, "Pagamento:", forma_pagamento)
        y = self._desenhar_campo(c, y, "Emissão:", data_emissao.strftime("%d/%m/%Y %H:%M"))
        y = self._desenhar_campo(c, y, "Atendente:", atendente_nome)

        # RODAPÉ
        self._desenhar_rodape(c, y)

        # Finaliza o PDF
        c.showPage()
        c.save()

        # Converte para base64
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return base64.b64encode(pdf_bytes).decode('utf-8')

    def _desenhar_cabecalho(self, c: canvas.Canvas, y: float) -> float:
        """Desenha o cabeçalho do PDF"""
        # Nome da empresa
        c.setFont("Helvetica-Bold", 16)
        texto = "EXPRESSO EMBUIBE"
        largura_texto = c.stringWidth(texto, "Helvetica-Bold", 16)
        x = (self.page_width - largura_texto) / 2
        c.drawString(x, y, texto)
        y -= 20

        # Linha separadora
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(self.margin, y, self.page_width - self.margin, y)
        y -= 15

        return y

    def _desenhar_numero_passagem(self, c: canvas.Canvas, y: float, numero: int) -> float:
        """Desenha o número da passagem em destaque"""
        c.setFont("Helvetica-Bold", 14)
        texto = f"Passagem Nº {numero}"
        largura_texto = c.stringWidth(texto, "Helvetica-Bold", 14)
        x = (self.page_width - largura_texto) / 2
        c.drawString(x, y, texto)
        y -= 20

        return y

    def _desenhar_campo(self, c: canvas.Canvas, y: float, label: str, valor: str) -> float:
        """Desenha um campo de dados"""
        x = self.margin

        # Label em negrito
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x, y, label)

        # Valor normal
        c.setFont("Helvetica", 9)
        label_width = c.stringWidth(label, "Helvetica-Bold", 9)
        c.drawString(x + label_width + 5, y, valor)

        y -= 12

        return y

    def _desenhar_rodape(self, c: canvas.Canvas, y: float):
        """Desenha o rodapé do PDF"""
        # Linha separadora
        y -= 10
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(self.margin, y, self.page_width - self.margin, y)
        y -= 15

        # Texto de instrução
        c.setFont("Helvetica", 8)
        texto = "Apresente este documento ao motorista no momento do embarque."
        largura_texto = c.stringWidth(texto, "Helvetica", 8)
        x = (self.page_width - largura_texto) / 2
        c.drawString(x, y, texto)


# Instância global do serviço
pdf_service = PDFService()
