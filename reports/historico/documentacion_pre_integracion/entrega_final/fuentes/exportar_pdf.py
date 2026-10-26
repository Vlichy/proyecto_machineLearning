"""Exporta la memoria Markdown a PDF; no usa dependencias de modelado."""
from pathlib import Path
import re,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4

OUT=Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('Arial',r'C:\Windows\Fonts\arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold',r'C:\Windows\Fonts\arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyA',fontName='Arial',fontSize=10.3,leading=15,spaceAfter=9,textColor=colors.HexColor('#243746')))
styles.add(ParagraphStyle(name='H1A',fontName='Arial-Bold',fontSize=30,leading=37,spaceAfter=24,textColor=colors.HexColor('#163d56')))
styles.add(ParagraphStyle(name='H2A',fontName='Arial-Bold',fontSize=17,leading=22,spaceBefore=17,spaceAfter=11,keepWithNext=True,textColor=colors.HexColor('#163d56')))
styles.add(ParagraphStyle(name='H3A',fontName='Arial-Bold',fontSize=12,leading=17,spaceBefore=12,spaceAfter=8,keepWithNext=True,textColor=colors.HexColor('#168880')))
styles.add(ParagraphStyle(name='CellA',fontName='Arial',fontSize=8.4,leading=11,spaceAfter=0))
styles.add(ParagraphStyle(name='CaptionA',parent=styles['BodyA'],fontSize=8.6,leading=12,textColor=colors.HexColor('#526674'),spaceAfter=13))
def inline(s):
    s=html.escape(s.replace('−','-').replace('–','-').replace('—','-'))
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    return s
lines=(OUT/'memoria_final.md').read_text(encoding='utf-8').splitlines();story=[];i=0;cover=True
while i<len(lines):
    line=lines[i].strip()
    if not line:i+=1;continue
    if line.startswith('# '):story.extend([Spacer(1,85),Paragraph(inline(line[2:]),styles['H1A'])]);i+=1;continue
    if line.startswith('## '):
        if line=='## Resumen ejecutivo':
            story.append(Spacer(1,25));story.append(Paragraph('Contenido: introducción y objetivos, dataset y EDA, preparación, metodología temporal, comparación, optimización y explicabilidad, selección, evaluación final, limitaciones, conclusiones y referencias.',styles['BodyA']));story.append(PageBreak());cover=False
        story.append(Paragraph(inline(line[3:]),styles['H2A']));i+=1;continue
    if line.startswith('### '):story.append(Paragraph(inline(line[4:]),styles['H3A']));i+=1;continue
    if line.startswith('!['):
        image_path=OUT/re.search(r'\]\((.*?)\)',line).group(1);w,h=ImageReader(str(image_path)).getSize();width=475;height=width*h/w
        image=Image(str(image_path),width=width,height=height)
        j=i+1
        while j<len(lines) and not lines[j].strip():j+=1
        if j<len(lines) and lines[j].startswith('Figura '):story.append(KeepTogether([image,Spacer(1,5),Paragraph(inline(lines[j]),styles['CaptionA'])]));i=j+1
        else:story.append(image);i+=1
        continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            row=[s.strip() for s in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',s) for s in row):rows.append(row)
            i+=1
        n=len(rows[0]); widths=[475/n]*n
        if n>=4:widths=[140]+[(475-140)/(n-1)]*(n-1)
        if n==8:widths=[65,63,63,63,45,45,65,66]
        table=Table([[Paragraph(inline(s),styles['CellA']) for s in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4eff2')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.8,colors.HexColor('#168880')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d7dfe3'))]));story.extend([table,Spacer(1,12)]);continue
    paragraph=[line];i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','![')):paragraph.append(lines[i].strip());i+=1
    story.append(Paragraph(inline(' '.join(paragraph)),styles['BodyA']))
def page(canvas,doc):
    canvas.saveState();canvas.setFont('Arial',8);canvas.setFillColor(colors.HexColor('#526674'));canvas.drawString(60,30,'Cancelaciones hoteleras · Memoria académica · Protocolo v3');canvas.drawRightString(A4[0]-60,30,str(doc.page));canvas.restoreState()
doc=SimpleDocTemplate(str(OUT/'memoria_final.pdf'),pagesize=A4,rightMargin=60,leftMargin=60,topMargin=48,bottomMargin=52,title='Predicción de cancelaciones hoteleras',author='Autoría académica no confirmada',subject='Memoria final retrospectiva v3')
doc.build(story,onFirstPage=page,onLaterPages=page)
print('PDF generado desde memoria_final.md')
