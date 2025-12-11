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


    def gerar_manifesto_viagem_pdf(
        self,
        numero_viagem: int,
        data_viagem: str,
        horario_programado: str,
        horario_saida: str,
        motorista_nome: str,
        proprietario_nome: str,
        passageiros: list,
        total_passageiros: int,
        valor_total: Decimal
    ) -> str:
        """
        Gera o PDF do manifesto de viagem

        Args:
            numero_viagem: ID da viagem
            data_viagem: Data da viagem formatada
            horario_programado: Horário programado
            horario_saida: Horário de saída real
            motorista_nome: Nome do motorista
            proprietario_nome: Nome do proprietário do veículo
            passageiros: Lista de passageiros
            total_passageiros: Total de passageiros
            valor_total: Valor total da viagem

        Returns:
            PDF em base64
        """
        from reportlab.lib.pagesizes import A4

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        page_width, page_height = A4

        y = page_height - 30

        # CABEÇALHO
        c.setFont("Helvetica-Bold", 18)
        texto = "EXPRESSO EMBUIBE"
        largura_texto = c.stringWidth(texto, "Helvetica-Bold", 18)
        x = (page_width - largura_texto) / 2
        c.drawString(x, y, texto)
        y -= 25

        c.setFont("Helvetica-Bold", 14)
        texto = "MANIFESTO DE VIAGEM"
        largura_texto = c.stringWidth(texto, "Helvetica-Bold", 14)
        x = (page_width - largura_texto) / 2
        c.drawString(x, y, texto)
        y -= 20

        # Linha separadora
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.line(40, y, page_width - 40, y)
        y -= 25

        # DADOS DA VIAGEM
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, f"Viagem Nº: {numero_viagem}")
        c.drawString(250, y, f"Data: {data_viagem}")
        y -= 18

        c.drawString(40, y, f"Horário Programado: {horario_programado}")
        c.drawString(250, y, f"Horário de Saída: {horario_saida}")
        y -= 18

        c.drawString(40, y, f"Motorista: {motorista_nome}")
        y -= 18

        c.drawString(40, y, f"Proprietário: {proprietario_nome}")
        y -= 25

        # Linha separadora
        c.setLineWidth(1)
        c.line(40, y, page_width - 40, y)
        y -= 20

        # TABELA DE PASSAGEIROS
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y, "#")
        c.drawString(60, y, "Passageiro")
        c.drawString(250, y, "Origem")
        c.drawString(350, y, "Local Embarque")
        c.drawString(490, y, "Valor")
        y -= 5

        c.setLineWidth(0.5)
        c.line(40, y, page_width - 40, y)
        y -= 15

        c.setFont("Helvetica", 9)
        for idx, p in enumerate(passageiros, 1):
            if y < 100:  # Nova página se necessário
                c.showPage()
                y = page_height - 50
                c.setFont("Helvetica", 9)

            c.drawString(40, y, str(idx))
            # Truncar nome se muito grande
            nome = p.get('cliente_nome', p.get('nome', 'N/A'))[:30]
            c.drawString(60, y, nome)
            c.drawString(250, y, p.get('cidade', 'N/A')[:15])
            c.drawString(350, y, p.get('local_embarque', 'N/A')[:20])
            valor = p.get('valor', 0)
            c.drawString(490, y, f"R$ {valor:.2f}")
            y -= 14

        # TOTAIS
        y -= 10
        c.setLineWidth(1)
        c.line(40, y, page_width - 40, y)
        y -= 20

        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, f"TOTAL DE PASSAGEIROS: {total_passageiros}")
        c.drawString(350, y, f"VALOR TOTAL: R$ {valor_total:.2f}")
        y -= 30

        # RODAPÉ
        c.setLineWidth(2)
        c.line(40, y, page_width - 40, y)
        y -= 20

        c.setFont("Helvetica", 8)
        texto = f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
        c.drawString(40, y, texto)
        y -= 12
        texto = "Este documento é o registro oficial da viagem."
        c.drawString(40, y, texto)

        c.showPage()
        c.save()

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return base64.b64encode(pdf_bytes).decode('utf-8')


# Instância global do serviço
pdf_service = PDFService()
