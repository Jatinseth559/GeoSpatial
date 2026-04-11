from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import text
from core.database import engine
import json
import os

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.get("/weights")
async def get_weight_configurations():
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT id, config_name, use_case, weights, thresholds, is_default
            FROM weight_configurations
            ORDER BY is_default DESC
        """))
        
        rows = result.fetchall()
        
        configs = []
        for row in rows:
            configs.append({
                "id": row[0],
                "config_name": row[1],
                "use_case": row[2],
                "weights": json.loads(row[3]) if row[3] else {},
                "thresholds": json.loads(row[4]) if row[4] else {},
                "is_default": row[5]
            })
        
        return configs


@router.get("/site-report/{site_id}")
async def export_site_report(site_id: int):
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT id, site_name, description, latitude, longitude,
                   composite_score, score_breakdown, weights_used,
                   catchment_pop_10min, catchment_pop_20min, catchment_pop_30min
            FROM candidate_sites
            WHERE id = :id
        """), {"id": site_id})
        
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Site not found")
        
        site_data = {
            "id": row[0],
            "site_name": row[1],
            "description": row[2],
            "latitude": row[3],
            "longitude": row[4],
            "composite_score": row[5],
            "score_breakdown": json.loads(row[6]) if row[6] else {},
            "weights_used": json.loads(row[7]) if row[7] else {},
            "catchment_pop_10min": row[8],
            "catchment_pop_20min": row[9],
            "catchment_pop_30min": row[10]
        }
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        output_dir = "/tmp"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"site_report_{site_id}.pdf")
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor("#1a1d29")
        )
        
        elements.append(Paragraph(f"Site Readiness Report: {site_data['site_name']}", title_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("<b>Composite Score:</b> " + f"{site_data['composite_score']:.1f}/100", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        if site_data['score_breakdown']:
            data = [[c.capitalize(), f"{v:.1f}"] for c, v in site_data['score_breakdown'].items()]
            data.insert(0, ["Category", "Score"])
            
            table = Table(data, colWidths=[200, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#6366f1")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("<b>Catchment Population:</b>", styles['Normal']))
        pop_data = [["10 min", "20 min", "30 min"]]
        pop_data.append([
            str(site_data.get('catchment_pop_10min', 0)),
            str(site_data.get('catchment_pop_20min', 0)),
            str(site_data.get('catchment_pop_30min', 0))
        ])
        
        pop_table = Table(pop_data, colWidths=[100, 100, 100])
        pop_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#10b981")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(pop_table)
        
        doc.build(elements)
        
        return FileResponse(output_path, media_type="application/pdf", 
                          filename=f"site_report_{site_id}.pdf")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")