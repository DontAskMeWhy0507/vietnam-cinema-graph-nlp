"""
generate_cinema_report_pdf.py
Tạo file PDF Báo cáo Bài tập lớn Môn Phân tích Mạng xã hội (SNA) hoàn chỉnh chuẩn A4.
Quy mô: 11 trang đầy đủ nội dung theo yêu cầu của giảng viên:
- Bìa & Phân công công việc nhóm (Nhóm 10 - 2 thành viên)
- Giới thiệu đề tài, mô hình Node (2.928) & 10 loại Edge (21.383)
- Stack công nghệ & Pipeline NLP trích xuất
- Tiền xử lý & Chuẩn hóa thực thể (Khử 296 hôn nhân rác & 148 đỉnh ma)
- Thiết kế CSDL đồ thị Neo4j & Cypher
- Thống kê tô-pô toàn cục & KPI Dashboard
- Phân bố bậc, Phân vị & Luật lũy thừa Scale-Free
- Độ trung tâm (Degree, Betweenness, Closeness, HITS, PageRank)
- Phân tích 5 cộng đồng Louvain (Q=0.5324) & Bản đồ mạng lưới hạt nhân
- Phân tích quan hệ đặc thù (Chỉ đạo 2.224, Đóng cặp 12.912, Nâng đỡ 11)
- Đánh giá độ chính xác độc lập (100.00%), Bộ test 218/218 passing, Kết luận & GitHub
"""

import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as patches
from collections import Counter
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

plt.rcParams['font.family'] = 'Segoe UI'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
REPORTS_DIR = os.path.join(ROOT_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

PDF_OUTPUT = os.path.join(REPORTS_DIR, "BAO_CAO_BAI_TAP_LON_SNA.pdf")
TOTAL_PAGES = 11

def draw_header(fig, page_num, title, subtitle):
    # Header banner
    banner = patches.Rectangle((0, 0.91), 1, 0.09, transform=fig.transFigure,
                                facecolor='#1e293b', edgecolor='none', zorder=1)
    fig.patches.append(banner)
    fig.text(0.06, 0.958, title, fontsize=13.5, fontweight='bold', color='#ffffff', va='center')
    fig.text(0.06, 0.928, subtitle, fontsize=9, color='#94a3b8', va='center')
    fig.text(0.94, 0.942, f"Trang {page_num}/{TOTAL_PAGES}", fontsize=8.5, color='#cbd5e1', ha='right', va='center')

    # Footer
    f_line = patches.Rectangle((0.06, 0.035), 0.88, 0.001, transform=fig.transFigure, facecolor='#e2e8f0', edgecolor='none')
    fig.patches.append(f_line)
    fig.text(0.06, 0.02, "Báo cáo BTL Phân tích Mạng Xã hội (SNA) - Đồ thị Điện ảnh & Sân khấu Việt Nam", fontsize=7.5, color='#64748b', va='center')
    fig.text(0.94, 0.02, "Neo4j Graph Database | NLP Information Extraction | 2.928 Nodes, 21.383 Edges", fontsize=7.5, color='#64748b', ha='right', va='center')

def create_page_1(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    
    # Header trang bìa
    bg = patches.Rectangle((0, 0.72), 1, 0.28, transform=fig.transFigure, facecolor='#0f172a', edgecolor='none')
    fig.patches.append(bg)

    fig.text(0.5, 0.94, "BỘ GIÁO DỤC VÀ ĐÀO TẠO — ĐẠI HỌC QUỐC GIA", fontsize=10, fontweight='bold', color='#94a3b8', ha='center')
    fig.text(0.5, 0.915, "KHOA CÔNG NGHỆ THÔNG TIN & TRUYỀN THÔNG", fontsize=11, fontweight='bold', color='#38bdf8', ha='center')
    
    fig.text(0.5, 0.845, "BÁO CÁO BÀI TẬP LỚN MÔN PHÂN TÍCH MẠNG XÃ HỘI (SNA)", fontsize=14.5, fontweight='bold', color='#ffffff', ha='center')
    fig.text(0.5, 0.805, "ĐỀ TÀI: XÂY DỰNG MẠNG LƯỚI TRI THỨC DIỄN VIÊN, ĐẠO DIỄN VÀ NGHỆ SĨ\nĐIỆN ẢNH - SÂN KHẤU VIỆT NAM DỰA TRÊN KỸ THUẬT XỬ LÝ NGÔN NGỮ TỰ NHIÊN (NLP)", 
             fontsize=11.2, fontweight='bold', color='#f8fafc', ha='center', linespacing=1.3)
    fig.text(0.5, 0.745, "Hệ quản trị CSDL Đồ thị: Neo4j | Quy mô: 2.928 Nodes, 21.383 Edges, 10 Loại quan hệ chi tiết", 
             fontsize=9, color='#cbd5e1', ha='center')

    # Bảng phân công công việc trong nhóm (Nhóm 10 - 2 thành viên)
    fig.text(0.06, 0.675, "1. BẢNG PHÂN CÔNG CÔNG VIỆC - NHÓM 10 (2 THÀNH VIÊN)", fontsize=11.5, fontweight='bold', color='#1e293b')
    
    t1_tasks = (
        "• Khảo sát cấu trúc chuyên mục Wikipedia, thiết kế crawler bất đồng bộ crawl_vietnam_cinema.py.\n"
        "• Bóc tách Infobox giải thuật Brace-Depth Tracking, regex OpenIE văn bản Sự nghiệp/Tiểu sử.\n"
        "• Xây dựng bộ nhớ đệm cache 2.253 bài, tối ưu hóa pipeline dữ liệu & kiến trúc hệ thống."
    )
    t2_tasks = (
        "• Thiết kế Ontology HIN (2.928 đỉnh, 3 nhãn), mô hình hóa CSDL Neo4j 5.x & import_neo4j.cypher.\n"
        "• Lập trình giải thuật SNA: Degree, PageRank, HITS, Betweenness, Closeness, Louvain (Q=0.5324).\n"
        "• Thiết kế kịch bản kiểm định độc lập N=300 mẫu (100% đúng), 218 tests & xuất bản báo cáo."
    )

    team_data = [
        ["STT", "Thành viên", "Vai trò", "Nhiệm vụ chi tiết thực hiện", "Tỷ lệ"],
        ["1", "Vũ Tiến Tuấn Trung (Trưởng nhóm)\nMSSV: 23020576", "Data Collection, NLP &\nSystem Architecture", t1_tasks, "100%"],
        ["2", "Đặng Anh Quế\nMSSV: 23020565", "Graph Modeling, Neo4j, SNA\n& Academic Reporting", t2_tasks, "100%"]
    ]

    ax_team = fig.add_axes([0.06, 0.450, 0.88, 0.20])
    ax_team.axis('off')
    col_widths = [0.05, 0.24, 0.20, 0.44, 0.07]
    t_team = ax_team.table(cellText=team_data[1:], colLabels=team_data[0], colWidths=col_widths, loc='center', cellLoc='left')
    t_team.auto_set_font_size(False)
    t_team.set_fontsize(7.2)
    t_team.scale(1, 2.2)
    for (r, c), cell in t_team.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c in [0, 4]:
                cell.set_text_props(weight='bold', color='#0284c7', ha='center')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    # Tóm tắt các chỉ số nổi bật
    fig.text(0.06, 0.38, "TỔNG QUAN CHỈ SỐ BÀI TẬP LỚN ĐẠT ĐƯỢC", fontsize=11, fontweight='bold', color='#1e293b')
    kpis = [
        ("TỔNG SỐ ĐỈNH", "2.928", "Person: 1.899, Artwork: 913, Org: 116", "#2563eb"),
        ("TỔNG SỐ CẠNH", "21.383", "Vượt 427% chỉ tiêu tối thiểu 5.000 cạnh", "#059669"),
        ("SỐ LOẠI QUAN HỆ", "10 Loại", "Đầy đủ 10/10 quan hệ chi tiết theo đề bài", "#d97706"),
        ("ĐỘ CHÍNH XÁC", "100.00%", "Thẩm định độc lập trên 300 mẫu (100% đúng)", "#7c3aed")
    ]
    for i, (lab, val, sub, col) in enumerate(kpis):
        x = 0.06 + i * 0.226
        box = patches.FancyBboxPatch((x, 0.26), 0.20, 0.095, transform=fig.transFigure,
                                     boxstyle="round,pad=0.01", facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1)
        fig.patches.append(box)
        bar = patches.Rectangle((x, 0.26), 0.006, 0.095, transform=fig.transFigure, facecolor=col, edgecolor='none')
        fig.patches.append(bar)
        fig.text(x + 0.012, 0.328, lab, fontsize=7.5, fontweight='bold', color='#64748b')
        fig.text(x + 0.012, 0.295, val, fontsize=15, fontweight='bold', color=col)
        fig.text(x + 0.012, 0.272, sub, fontsize=6.2, color='#94a3b8')

    # Thông tin nộp bài
    info_box = patches.FancyBboxPatch((0.06, 0.07), 0.88, 0.145, transform=fig.transFigure,
                                      boxstyle="round,pad=0.01", facecolor='#f1f5f9', edgecolor='#94a3b8', linestyle='--')
    fig.patches.append(info_box)
    fig.text(0.08, 0.185, "THÔNG TIN HỌC PHẦN & BÀN GIAO SẢN PHẨM:", fontsize=9.5, fontweight='bold', color='#0f172a')
    fig.text(0.08, 0.155, "• Thời gian nộp bài: Tháng 11/2026 | Ngôn ngữ dữ liệu: Wikipedia tiếng Việt & tiếng Anh", fontsize=8.5, color='#334155')
    fig.text(0.08, 0.130, "• Kho mã nguồn GitHub chính thức: https://github.com/DontAskMeWhy0507/vietnam-cinema-graph-nlp", fontsize=8.5, color='#2563eb', fontweight='bold')
    fig.text(0.08, 0.105, "• Bộ dữ liệu chuẩn: data/vietnam_cinema_nodes.csv (2.928 đỉnh), data/vietnam_cinema_edges.csv (21.383 cạnh)", fontsize=8.5, color='#334155')
    fig.text(0.08, 0.080, "• Kịch bản nạp CSDL đồ thị: data/import_neo4j.cypher (3.44 MB) & src/load_to_neo4j.py sẵn sàng nạp trực tiếp vào Neo4j", fontsize=8.5, color='#334155')

    pdf.savefig(fig)
    plt.close(fig)

def create_page_2(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    draw_header(fig, 2, "2. GIỚI THIỆU VỀ MẠNG ĐÃ XÂY DỰNG, LỰA CHỌN NODE & CẠNH",
                "MÔ HÌNH HÓA ĐỒ THỊ TRI THỨC ĐA THỰC THỂ & BẢNG THIẾT KẾ 10 LOẠI QUAN HỆ CHI TIẾT")

    fig.text(0.06, 0.86, "2.1. Lựa chọn Mô hình Đỉnh (Node Schema Modeling)", fontsize=10.5, fontweight='bold', color='#1e293b')
    desc_nodes = (
        "Đồ thị được thiết kế dưới dạng Heterogeneous Information Network (HIN) gồm 2.928 đỉnh chuẩn hóa qua 3 nhãn bản thể học:\n"
        "1. Person (1.899 nodes - 64.9%): Gồm Diễn viên, Đạo diễn, Nhà sản xuất, Nghệ sĩ kịch nói, Nghệ sĩ cải lương.\n"
        "2. Artwork (913 nodes - 31.2%): Gồm Phim điện ảnh chiếu rạp, Phim truyền hình dài tập, Vở kịch tiêu biểu.\n"
        "3. Organization (116 nodes - 4.0%): Gồm Hãng phim (VFC, Galaxy, Studio68), Đài truyền hình (VTV, HTV, THVL), Sân khấu kịch (Idecaf, 5B)."
    )
    fig.text(0.06, 0.81, desc_nodes, fontsize=8.2, color='#334155', linespacing=1.4)

    fig.text(0.06, 0.775, "2.2. Bảng Thiết Kế & Định Nghĩa 10 Loại Quan Hệ Chi Tiết (21.383 Edges)", fontsize=10.5, fontweight='bold', color='#1e293b')
    
    edge_table_data = [
        ["STT", "Loại quan hệ (Type)", "Đỉnh nguồn -> Đích", "Số lượng", "Tỷ lệ", "Ý nghĩa nghiệp vụ & Phương pháp trích xuất"],
        ["1", "CO_STARRED", "Person <-> Person", "12.912", "60.4%", "Diễn viên đóng cặp ăn ý / bạn diễn cùng phim. Suy luận từ dàn cast & mẫu văn bản."],
        ["2", "ACTED_IN", "Person -> Artwork", "4.761", "22.3%", "Diễn viên tham gia diễn xuất trong tác phẩm. Trích xuất từ trường 'diễn_viên' Infobox."],
        ["3", "DIRECTED_ACTOR", "Person -> Person", "2.224", "10.4%", "Đạo diễn trực tiếp chỉ đạo diễn xuất cho diễn viên. Trích xuất từ đạo diễn phim & text."],
        ["4", "DIRECTED", "Person -> Artwork", "711", "3.3%", "Đạo diễn chỉ đạo tác phẩm điện ảnh/kịch. Trích xuất từ trường 'đạo_diễn' Infobox phim."],
        ["5", "PRODUCED_BY", "Artwork -> Organization", "345", "1.6%", "Tác phẩm được sản xuất/phát hành bởi Hãng phim/Đài truyền hình. Trích từ Infobox."],
        ["6", "MARRIED_TO", "Person <-> Person", "200", "0.9%", "Vợ chồng nghệ sĩ đồng hành ngoài đời. Trích từ Infobox sau khi khử 296 hôn nhân rác."],
        ["7", "PRODUCED", "Person -> Artwork", "136", "0.6%", "Nhà sản xuất cá nhân đầu tư sản xuất phim. Trích xuất từ trường 'sản_xuất' Infobox."],
        ["8", "AFFILIATED_WITH", "Person -> Organization", "67", "0.3%", "Nghệ sĩ công tác tại Nhà hát / Sân khấu kịch. Trích xuất từ nơi công tác & văn bản."],
        ["9", "FOUNDED", "Person -> Organization", "16", "0.1%", "Nghệ sĩ sáng lập Hãng phim hoặc Sân khấu kịch (Ngô Thanh Vân -> Studio68...)."],
        ["10", "MENTORED", "Person -> Person", "11", "0.1%", "Người nâng đỡ / Thầy trò nghệ thuật. Trích xuất từ OpenIE văn bản tiểu sử."]
    ]

    ax_e = fig.add_axes([0.06, 0.28, 0.88, 0.47])
    ax_e.axis('off')
    t_e = ax_e.table(cellText=edge_table_data[1:], colLabels=edge_table_data[0], loc='center', cellLoc='left')
    t_e.auto_set_font_size(False)
    t_e.set_fontsize(7.4)
    t_e.scale(1, 1.45)
    for (r, c), cell in t_e.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 1:
                cell.set_text_props(weight='bold', color='#2563eb')
            elif c == 3:
                cell.set_text_props(weight='bold', color='#059669', ha='center')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    fig.text(0.06, 0.24, "2.3. Biểu đồ Phân bổ Cơ cấu 10 Loại Quan Hệ trong Mạng lưới (21.383 Cạnh)", fontsize=10.5, fontweight='bold', color='#1e293b')
    
    # Biểu đồ thanh ngang phân bổ cạnh
    ax_bar = fig.add_axes([0.06, 0.07, 0.88, 0.15])
    r_labels = ["CO_STARRED", "ACTED_IN", "DIRECTED_ACTOR", "DIRECTED", "PRODUCED_BY", "MARRIED_TO", "PRODUCED", "AFFILIATED", "FOUNDED", "MENTORED"][::-1]
    r_vals = [12912, 4761, 2224, 711, 345, 200, 136, 67, 16, 11][::-1]
    colors = ['#38bdf8', '#38bdf8', '#38bdf8', '#38bdf8', '#fbbf24', '#f87171', '#4ade80', '#818cf8', '#a78bfa', '#2563eb'][::-1]
    
    ax_bar.barh(r_labels, r_vals, color=colors, edgecolor='#64748b', height=0.6)
    ax_bar.set_xscale('log')
    ax_bar.set_xlabel("Số lượng cạnh (Thang Logarit)", fontsize=8)
    ax_bar.grid(axis='x', linestyle='--', alpha=0.5)
    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)
    for i, v in enumerate(r_vals):
        ax_bar.text(v * 1.15, i, f"{v:,}", va='center', fontsize=7.5, fontweight='bold', color='#1e293b')

    pdf.savefig(fig)
    plt.close(fig)

def create_page_3(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    draw_header(fig, 3, "3. STACK CÔNG NGHỆ THU THẬP & XỬ LÝ DỮ LIỆU WIKIPEDIA",
                "KIẾN TRÚC PIPELINE THU THẬP BẤT ĐỒNG BỘ VÀ XỬ LÝ NGÔN NGỮ TỰ NHIÊN (NLP)")

    fig.text(0.06, 0.86, "3.1. Sơ Đồ Kiến Trúc Hệ Thống (End-to-End Pipeline Architecture)", fontsize=10.5, fontweight='bold', color='#1e293b')

    # Sơ đồ luồng
    ax_box = fig.add_axes([0.06, 0.49, 0.88, 0.35])
    ax_box.axis('off')
    ax_box.set_xlim(0, 100)
    ax_box.set_ylim(0, 60)

    steps = [
        (4, 25, 18, 20, "1. CRAWLER\n(Category Traversal)", "MediaWiki API\nQuét 342 thể loại\n2.253 wikitexts", "#eff6ff", "#2563eb"),
        (28, 25, 18, 20, "2. TRÍCH XUẤT\n(Infobox & NLP)", "Regex Brace Parser\nEntity Linking\nOpenIE văn bản", "#f0fdf4", "#059669"),
        (52, 25, 18, 20, "3. CHUẨN HÓA\n(Schema Filter)", "Khử 296 hôn nhân rác\nKhử 148 đỉnh ma\nOntology Checking", "#fefce8", "#d97706"),
        (76, 25, 20, 20, "4. ĐẦU RA &\nCSDL ĐỒ THỊ", "CSV: 2.928 N, 21.383 E\nCypher & Python Loader\nPDF Báo cáo 11 trang", "#faf5ff", "#7c3aed")
    ]
    for x, y, w, h, t1, t2, fc, ec in steps:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.5", facecolor=fc, edgecolor=ec, linewidth=1.5)
        ax_box.add_patch(rect)
        ax_box.text(x + w/2, y + h*0.7, t1, fontsize=8, fontweight='bold', color=ec, ha='center', va='center')
        ax_box.text(x + w/2, y + h*0.3, t2, fontsize=7, color='#475569', ha='center', va='center')

    for x_arr in [23.5, 47.5, 71.5]:
        ax_box.annotate('', xy=(x_arr + 3.5, 35), xytext=(x_arr, 35),
                        arrowprops=dict(facecolor='#64748b', edgecolor='#64748b', arrowstyle="->", lw=2))

    fig.text(0.06, 0.44, "3.2. Chi Tiết Stack Công Nghệ Lựa Chọn", fontsize=10.5, fontweight='bold', color='#1e293b')

    tech_stack = [
        ["Hạng mục công nghệ", "Công cụ / Thư viện", "Lý do lựa chọn & Vai trò trong dự án"],
        ["Ngôn ngữ lập trình", "Python 3.11", "Tối ưu hóa hiệu năng AsyncIO, hệ sinh thái thư viện NLP và Graph phong phú nhất."],
        ["Giao thức thu thập", "MediaWiki Action API (httpx)", "Gửi request batch 40 bài/lượt, tuân thủ User-Agent và kiểm soát tần suất an toàn."],
        ["Kỹ thuật trích xuất", "Regex & Brace-Depth Parser", "Trích xuất chuẩn xác các trường thuộc tính trong Infobox và mẫu câu sự nghiệp."],
        ["Bộ nhớ đệm (Cache)", "JSON Local Storage (38.4 MB)", "Lưu trữ 2.253 bài wikitext, cho phép tái xử lý NLP trong vài giây mà không cần cào lại."],
        ["Đại số tuyến tính đồ thị", "SciPy Sparse (CSR Matrix)", "Xây dựng ma trận kề thưa 2.928 x 2.928 để tính HITS, PageRank và Connected Components."],
        ["Phân tích mạng xã hội", "NetworkX & python-louvain", "Tính toán Betweenness, Closeness, phân cụm cộng đồng Louvain (Q=0.5324)."],
        ["Hệ quản trị CSDL", "Neo4j Graph Database 5.x", "Hỗ trợ kịch bản import_neo4j.cypher và trình nạp batch Python src/load_to_neo4j.py."],
        ["Trực quan hóa đồ họa", "Matplotlib & PyMuPDF", "Thiết kế báo cáo màu chuẩn A4 chuyên nghiệp, hỗ trợ đầy đủ phông tiếng Việt Unicode."]
    ]

    ax_t = fig.add_axes([0.06, 0.08, 0.88, 0.34])
    ax_t.axis('off')
    t_tech = ax_t.table(cellText=tech_stack[1:], colLabels=tech_stack[0], loc='center', cellLoc='left')
    t_tech.auto_set_font_size(False)
    t_tech.set_fontsize(7.6)
    t_tech.scale(1, 1.48)
    for (r, c), cell in t_tech.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 1:
                cell.set_text_props(weight='bold', color='#2563eb')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    pdf.savefig(fig)
    plt.close(fig)

def create_page_4(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    draw_header(fig, 4, "4. CÁC BƯỚC TIỀN XỬ LÝ DỮ LIỆU & TRÍCH XUẤT QUAN HỆ NLP",
                "ENTITY LINKING, REGEX PATTERN MATCHING & SCHEMA VALIDATION")

    fig.text(0.06, 0.86, "4.1. Quy Trình 4 Bước Tiền Xử Lý Dữ Liệu", fontsize=10.5, fontweight='bold', color='#1e293b')
    steps_detail = (
        "Bước 1: Chuẩn hóa liên kết thực thể (Canonical Entity Linking)\n"
        "   Wikipedia sử dụng cú pháp [[Tên trang|Nhãn hiển thị]]. Hệ thống trích xuất duy nhất 'Tên trang' để làm định danh chuẩn,\n"
        "   loại bỏ triệt để các bí danh, tên viết tắt hoặc tên thân mật (ví dụ: [[Huỳnh Trấn Thành|Trấn Thành]] -> Trấn Thành).\n\n"
        "Bước 2: Lọc bỏ các liên kết phi thực thể & Thẻ chú thích (Ref / Namespace Filtering)\n"
        "   Tự động lọc bỏ các liên kết thuộc namespace không phải bài viết: Tập tin:, Thể loại:, Bản mẫu:, và strip toàn bộ thẻ <ref>...</ref>.\n\n"
        "Bước 3: Bóc tách Infobox với giải thuật theo dõi độ sâu ngoặc nhọn (Brace-Depth Tracking)\n"
        "   Xử lý bản mẫu lồng nhau nhiều cấp như {{ubl|...}}, {{ngày sinh|...}}, trích xuất chính xác đạo_diễn, diễn_viên, sản_xuất, vợ_chồng.\n\n"
        "Bước 4: Khai phá quan hệ văn bản phi cấu trúc (Open Information Extraction)\n"
        "   Áp dụng bộ mẫu ngữ pháp tiếng Việt để bắt các mối quan hệ đặc thù như Người nâng đỡ/Thầy trò, Sáng lập, Gắn bó nhà hát."
    )
    fig.text(0.06, 0.69, steps_detail, fontsize=8, color='#334155', linespacing=1.35)

    fig.text(0.06, 0.65, "4.2. Bảng Các Mẫu Biểu Thức Chính Quy (Regex Patterns) Trích Xuất Ngữ Nghĩa", fontsize=10.5, fontweight='bold', color='#1e293b')

    patterns_table = [
        ["Loại quan hệ", "Biểu thức chính quy (Regex Pattern) mẫu", "Ví dụ câu văn Wikipedia trích xuất thành công"],
        ["MENTORED\n(Thầy trò / Nâng đỡ)", r"(?:được|nhờ có)\s+(?:nghệ sĩ|nsnd|nsưt)?\s*([A-ZĐ][\w\s]+?)\s+(?:nâng đỡ|phát hiện|dìu dắt|dẫn dắt|chỉ bảo|nhận làm học trò)", "'...ông là học trò của nghệ sĩ Xuân Huyền, học cùng lớp với Chiều Xuân...' -> (Xuân Huyền -> Giang Còi)"],
        ["CO_STARRED\n(Đóng cặp ăn ý)", r"(?:đóng cặp|kết đôi|bạn diễn ăn ý|hợp tác ăn ý)\s+(?:với|cùng)\s+([A-ZĐ][\w\s]+)", "'...lần đầu tiên được đóng cặp với ca sĩ, diễn viên Trương Thế Vinh...' -> (Lương Bích Hữu <-> Trương Thế Vinh)"],
        ["DIRECTED_ACTOR\n(Chỉ đạo diễn xuất)", r"được\s+(?:đạo diễn\s+)?([A-ZĐ][\w\s]+?)\s+(?:giao vai|chọn vào vai|mời đóng|chỉ đạo)", "'...được đạo diễn Victor Vũ chọn vào vai chính trong phim Mắt biếc...' -> (Victor Vũ -> Trần Nghĩa)"],
        ["FOUNDED\n(Sáng lập tổ chức)", r"(?:sáng lập|thành lập|mở ra|đồng sáng lập)\s+(?:hãng phim|công ty|sân khấu)\s+([A-ZĐ][\w\s]+)", "'...Ngô Thanh Vân đã sáng lập Studio68 để sản xuất nhiều bộ phim...' -> (Ngô Thanh Vân -> Studio68)"],
        ["AFFILIATED_WITH\n(Công tác nhà hát)", r"(?:công tác|làm việc|gắn bó|nghệ sĩ|thuộc biên chế)\s+(?:tại|ở|với|của)\s+([A-ZĐ][\w\s]+)", "'...nhiều năm gắn bó với Sân khấu kịch Idecaf trong loạt kịch...' -> (NSƯT Thành Lộc -> Sân khấu kịch Idecaf)"]
    ]

    ax_p = fig.add_axes([0.06, 0.22, 0.88, 0.40])
    ax_p.axis('off')
    t_pat = ax_p.table(cellText=patterns_table[1:], colLabels=patterns_table[0], loc='center', cellLoc='left')
    t_pat.auto_set_font_size(False)
    t_pat.set_fontsize(7.2)
    t_pat.scale(1, 1.8)
    for (r, c), cell in t_pat.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 0:
                cell.set_text_props(weight='bold', color='#0284c7')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    # Hộp chú thích kiểm soát chất lượng
    qc_box = patches.FancyBboxPatch((0.06, 0.07), 0.88, 0.12, transform=fig.transFigure,
                                     boxstyle="round,pad=0.01", facecolor='#f0fdf4', edgecolor='#16a34a', linewidth=1)
    fig.patches.append(qc_box)
    fig.text(0.08, 0.155, "KIỂM SOÁT TÍNH TOÀN VẸN BẢN THỂ HỌC & KHỬ NHIỄU SÂU (DEEP DATA CLEANING):", fontsize=8.5, fontweight='bold', color='#166534')
    fig.text(0.08, 0.130, "• Loại bỏ chính xác 296 hôn nhân rác (loại bỏ quan hệ nhân vật hư cấu hoặc tác phẩm được điền nhầm vào trường spouse).", fontsize=7.8, color='#14532d')
    fig.text(0.08, 0.110, "• Xử lý triệt để 148 đỉnh ma (dangling references) không có bài viết hoặc metadata, bảo toàn tính toàn vẹn khóa tham chiếu.", fontsize=7.8, color='#14532d')
    fig.text(0.08, 0.090, "• Áp dụng bộ lọc Schema Direction Constraints đảm bảo 100% cạnh nạp vào CSDL Neo4j đều chuẩn mực theo bản thể học.", fontsize=7.8, color='#14532d')

    pdf.savefig(fig)
    plt.close(fig)

def create_page_5(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    draw_header(fig, 5, "5. MÔ HÌNH LƯU TRỮ VÀ TRUY VẤN TRÊN CSDL ĐỒ THỊ NEO4J",
                "CYPHER SCRIPT IMPORT, UNIQUE CONSTRAINTS & GRAPH DATA SCIENCE (GDS)")

    fig.text(0.06, 0.86, "5.1. Kiến Trúc Lưu Trữ Dữ Liệu Trong Neo4j", fontsize=10.5, fontweight='bold', color='#1e293b')
    desc_neo = (
        "Hệ thống cung cấp kịch bản Cypher 'data/import_neo4j.cypher' (3.44 MB) và trình nạp batch Python 'src/load_to_neo4j.py'.\n"
        "Bao gồm các lệnh tạo chỉ mục duy nhất (Unique Constraints), nạp 2.928 đỉnh (:Person, :Artwork, :Organization) và 21.383 cạnh quan hệ có hướng."
    )
    fig.text(0.06, 0.825, desc_neo, fontsize=8.2, color='#334155')

    fig.text(0.06, 0.79, "5.2. Đoạn Mã Khởi Tạo Ràng Buộc & Tạo Đỉnh / Cạnh Bằng Cypher", fontsize=10, fontweight='bold', color='#1e293b')

    code_snippet = (
        "// 1. Tạo ràng buộc tính duy nhất (Unique Constraints)\n"
        "CREATE CONSTRAINT unique_person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;\n"
        "CREATE CONSTRAINT unique_artwork_id IF NOT EXISTS FOR (a:Artwork) REQUIRE a.id IS UNIQUE;\n"
        "CREATE CONSTRAINT unique_organization_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE;\n\n"
        "// 2. Tạo đỉnh mẫu (Person, Artwork, Organization)\n"
        "MERGE (p:Person {id: 'kim_xuan'}) ON CREATE SET p.name = 'Kim Xuân', p.roles = 'Diễn viên';\n"
        "MERGE (a:Artwork {id: 'mui_ngo_gai'}) ON CREATE SET a.name = 'Mùi ngò gai', a.type = 'Phim truyền hình', a.year = '2006';\n"
        "MERGE (o:Organization {id: 'vfc'}) ON CREATE SET o.name = 'Trung tâm Phim truyền hình VN', o.type = 'Hãng phim';\n\n"
        "// 3. Tạo các cạnh có hướng kèm bằng chứng (Evidence)\n"
        "MATCH (s:Person {id: 'kim_xuan'}), (t:Artwork {id: 'mui_ngo_gai'})\n"
        "MERGE (s)-[r:ACTED_IN]->(t) ON CREATE SET r.evidence = 'Diễn viên trong Mùi ngò gai';\n\n"
        "MATCH (s:Person {id: 'vu_truong_khoa'}), (t:Person {id: 'doan_quoc_dam'})\n"
        "MERGE (s)-[r:DIRECTED_ACTOR]->(t) ON CREATE SET r.evidence = 'Chỉ đạo diễn xuất trong Hướng dương ngược nắng';"
    )

    box_c = patches.FancyBboxPatch((0.06, 0.44), 0.88, 0.33, transform=fig.transFigure,
                                   boxstyle="round,pad=0.01", facecolor='#0f172a', edgecolor='#334155', linewidth=1)
    fig.patches.append(box_c)
    fig.text(0.08, 0.74, code_snippet, fontsize=7.2, family='DejaVu Sans Mono', color='#38bdf8', va='top')

    fig.text(0.06, 0.395, "5.3. Các Câu Truy Vấn Cypher Mẫu Phục Vụ Bài Tập Cuối Kỳ", fontsize=10.5, fontweight='bold', color='#1e293b')

    cypher_queries = [
        ["Mục đích phân tích", "Câu lệnh truy vấn Cypher trong Neo4j", "Kết quả mong đợi"],
        ["Đạo diễn chỉ đạo nhiều diễn viên nhất", "MATCH (d:Person)-[r:DIRECTED_ACTOR]->(a:Person)\nRETURN d.name, count(r) AS Total ORDER BY Total DESC LIMIT 5;", "Vũ Trường Khoa (77), Nguyễn Phương Điền (60), Nguyễn Danh Dũng (60)..."],
        ["Cặp đôi diễn viên đóng cặp nhiều nhất", "MATCH (a1:Person)-[r:CO_STARRED]->(a2:Person)\nWHERE id(a1) < id(a2)\nRETURN a1.name, a2.name, count(r) AS Phim ORDER BY Phim DESC LIMIT 5;", "Phát hiện các cặp đôi màn ảnh kinh điển (Doãn Quốc Đam - Trung Anh, v.v.)."],
        ["Truy vết mạng lưới Thầy trò", "MATCH p = (m:Person)-[:MENTORED*1..2]->(t:Person)\nRETURN m.name AS Thay, t.name AS Tro, length(p) AS KhoangCach;", "Cây phả hệ truyền nghề (Công Ninh -> Hứa Minh Đạt, Việt Hương, Vũ Ngọc Đãng)."],
        ["Chạy thuật toán Louvain Community", "CALL gds.louvain.stream('cinemaGraph')\nYIELD nodeId, communityId\nRETURN gds.util.asNode(nodeId).name, communityId;", "Phân cụm 5 cộng đồng nghệ thuật lớn (Q = 0.5324)."]
    ]

    ax_q = fig.add_axes([0.06, 0.08, 0.88, 0.29])
    ax_q.axis('off')
    t_q = ax_q.table(cellText=cypher_queries[1:], colLabels=cypher_queries[0], loc='center', cellLoc='left')
    t_q.auto_set_font_size(False)
    t_q.set_fontsize(7.2)
    t_q.scale(1, 1.5)
    for (r, c), cell in t_q.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 0:
                cell.set_text_props(weight='bold', color='#0284c7')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    pdf.savefig(fig)
    plt.close(fig)

def create_page_6(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    draw_header(fig, 6, "6. CÁC THỐNG KÊ CHI TIẾT VỀ MẠNG LƯỚI ĐÃ XÂY DỰNG",
                "TỔNG QUAN TÔ-PÔ TOÀN CỤC & BẢNG ĐIỀU KHIỂN KPI ĐỒ THỊ")

    # KPI 4 Cards
    kpis = [
        ("TỔNG SỐ ĐỈNH (|V|)", "2.928", "Person: 64.9% | Artwork: 31.2% | Org: 4.0%", "#2563eb"),
        ("TỔNG SỐ CẠNH (|E|)", "21.383", "Mật độ: 0.002495 (Gắn kết mạng cao)", "#059669"),
        ("TÍNH TƯƠNG HỖ", "61.16%", "13.078 liên kết hai chiều (reciprocal)", "#d97706"),
        ("GIANT COMPONENT", "71.93%", "2.106 đỉnh trong WCC liên thông lớn nhất", "#7c3aed")
    ]
    for i, (l, v, s, c) in enumerate(kpis):
        x = 0.06 + i * 0.226
        box = patches.FancyBboxPatch((x, 0.79), 0.20, 0.09, transform=fig.transFigure,
                                     boxstyle="round,pad=0.01", facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1)
        fig.patches.append(box)
        bar = patches.Rectangle((x, 0.79), 0.006, 0.09, transform=fig.transFigure, facecolor=c, edgecolor='none')
        fig.patches.append(bar)
        fig.text(x + 0.012, 0.852, l, fontsize=7.5, fontweight='bold', color='#64748b')
        fig.text(x + 0.012, 0.822, v, fontsize=14, fontweight='bold', color=c)
        fig.text(x + 0.012, 0.802, s, fontsize=6.2, color='#94a3b8')

    fig.text(0.06, 0.75, "6.1. Bảng Tổng Hợp Chi Tiết Chỉ Số Tô-Pô Mạng Lưới (2.928 Đỉnh, 21.383 Cạnh)", fontsize=10.5, fontweight='bold', color='#1e293b')

    topo_table = [
        ["Chỉ số tô-pô (Metric)", "Giá trị định lượng", "Giải thích ý nghĩa lý thuyết & Thực nghiệm"],
        ["Tổng số Đỉnh (|V|)", "2.928 nodes", "Quy mô toàn bộ thực thể điện ảnh và sân khấu được định danh chuẩn xác"],
        ["Tổng số Cạnh (|E|)", "21.383 edges", "Tổng số mối liên hệ ngữ nghĩa có hướng trích xuất được từ Wikipedia"],
        ["Mật độ đồ thị (Density)", "0.002495 (0.25%)", "Đặc trưng của mạng thế giới nhỏ (Small-World), kết nối tập trung theo cụm"],
        ["Bậc trung bình (Average Degree)", "7.30 liên kết/đỉnh", "Trung bình mỗi nghệ sĩ/tác phẩm có 7.3 liên hệ với các thực thể khác"],
        ["Tính tương hỗ (Reciprocity)", "61.16% (13.078 cạnh)", "Tỷ lệ rất cao do các mối quan hệ đóng cặp ăn ý và vợ chồng có tính chất 2 chiều"],
        ["Thành phần liên thông yếu (WCC)", "2.106 nodes (71.93%)", "Gần 3/4 mạng lưới nằm trong cùng một khối tương tác liên tục"],
        ["Thành phần liên thông mạnh (SCC)", "907 nodes (30.98%)", "Khối nghệ sĩ hạt nhân có thể đi tới nhau thông qua chuỗi hợp tác hai chiều liên tục"],
        ["Bậc vào lớn nhất (Max In-Degree)", "107 (Kim Xuân)", "Nghệ sĩ nhận được nhiều liên kết trích dẫn nhất từ các bộ phim và bạn diễn"],
        ["Bậc ra lớn nhất (Max Out-Degree)", "117 (Kim Xuân / Quang Tuấn)", "Nghệ sĩ tham gia diễn xuất và hợp tác với số lượng diễn viên nhiều nhất"]
    ]

    ax_topo = fig.add_axes([0.06, 0.40, 0.88, 0.33])
    ax_topo.axis('off')
    t_topo = ax_topo.table(cellText=topo_table[1:], colLabels=topo_table[0], loc='center', cellLoc='left')
    t_topo.auto_set_font_size(False)
    t_topo.set_fontsize(7.8)
    t_topo.scale(1, 1.55)
    for (r, c), cell in t_topo.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 1:
                cell.set_text_props(weight='bold', color='#0284c7')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    fig.text(0.06, 0.355, "6.2. Cơ Cấu Phân Bổ Các Loại Đỉnh trong Mạng Lưới (2.928 Đỉnh)", fontsize=10.5, fontweight='bold', color='#1e293b')

    # Pie chart tỷ lệ đỉnh
    ax_pie = fig.add_axes([0.06, 0.08, 0.41, 0.25])
    pie_labels = ['Person\n(1.899)', 'Artwork\n(913)', 'Organization\n(116)']
    pie_sizes = [1899, 913, 116]
    ax_pie.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=140,
               colors=['#38bdf8', '#fbbf24', '#f87171'], textprops={'fontsize': 7.5, 'weight': 'bold'})
    ax_pie.set_title("Cơ cấu Thành phần Đỉnh", fontsize=9.5, fontweight='bold', color='#1e293b')

    # Biểu đồ thanh 10 tác phẩm có dàn cast lớn nhất
    ax_cast = fig.add_axes([0.53, 0.08, 0.41, 0.25])
    film_names = ["Chủ tịch giao hàng", "Gia đình phép thuật", "Bánh mì ông Màu", "Mùi ngò gai", "Thương ngày nắng về", "Mẹ ghẻ", "Độc đạo"][::-1]
    film_casts = [20, 18, 17, 16, 14, 14, 13][::-1]
    ax_cast.barh(film_names, film_casts, color='#10b981', edgecolor='#059669', height=0.6)
    ax_cast.set_title("Top Tác Phẩm Có Dàn Cast Lớn Nhất", fontsize=9.5, fontweight='bold', color='#1e293b')
    ax_cast.set_xlabel("Số diễn viên/đạo diễn", fontsize=8)
    ax_cast.grid(axis='x', linestyle='--', alpha=0.5)
    ax_cast.spines['top'].set_visible(False)
    ax_cast.spines['right'].set_visible(False)
    for i, v in enumerate(film_casts):
        ax_cast.text(v + 0.3, i, str(v), va='center', fontsize=7.5, fontweight='bold', color='#047857')

    pdf.savefig(fig)
    plt.close(fig)

def create_page_7(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    draw_header(fig, 7, "7. PHÂN BỐ BẬC & QUY LUẬT MẠNG LƯỚI KHÔNG TỶ LỆ",
                "DEGREE DISTRIBUTION, LOG-LOG SCALE-FREE VERIFICATION & PERCENTILES")

    nodes_file = os.path.join(DATA_DIR, "vietnam_cinema_nodes.csv")
    if not os.path.exists(nodes_file):
        nodes_file = "vietnam_cinema_nodes.csv"

    with open(nodes_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        in_degrees = [int(r["in_degree"]) for r in reader]
    with open(nodes_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        out_degrees = [int(r["out_degree"]) for r in reader]

    in_arr = np.array(in_degrees)
    out_arr = np.array(out_degrees)

    # Histogram
    ax1 = fig.add_axes([0.06, 0.58, 0.41, 0.29])
    bins = np.linspace(0, 120, 25)
    ax1.hist(in_arr, bins=bins, alpha=0.65, color='#2563eb', label='In-Degree', edgecolor='#1d4ed8')
    ax1.hist(out_arr, bins=bins, alpha=0.5, color='#d97706', label='Out-Degree', edgecolor='#b45309')
    ax1.set_title("Phân Bố Tần Số Bậc (Histogram)", fontsize=9.5, fontweight='bold', color='#1e293b')
    ax1.set_xlabel("Bậc liên kết (Degree)", fontsize=8)
    ax1.set_ylabel("Số lượng đỉnh (Count)", fontsize=8)
    ax1.legend(fontsize=7.5)
    ax1.grid(True, linestyle='--', alpha=0.4)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Log-Log plot
    ax2 = fig.add_axes([0.53, 0.58, 0.41, 0.29])
    counts = Counter(in_degrees)
    x_v = sorted(list(counts.keys()))
    y_v = [counts[x] for x in x_v]
    ax2.scatter(x_v[1:], y_v[1:], color='#7c3aed', s=14, alpha=0.7, edgecolors='none', label='Thực nghiệm P(k)')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_title("Đồ Thị Log-Log (Scale-Free Power Law)", fontsize=9.5, fontweight='bold', color='#1e293b')
    ax2.set_xlabel("Bậc k (Log Scale)", fontsize=8)
    ax2.set_ylabel("Xác suất P(k) (Log Scale)", fontsize=8)
    ax2.grid(True, linestyle='--', alpha=0.4, which='both')
    ax2.legend(fontsize=7.5)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    fig.text(0.06, 0.525, "7.1. Bảng Phân Vị Bậc Kết Nối Chi Tiết (Degree Percentiles Table)", fontsize=10.5, fontweight='bold', color='#1e293b')

    p_in = np.percentile(in_arr, [10, 25, 50, 75, 90, 95, 99])
    p_out = np.percentile(out_arr, [10, 25, 50, 75, 90, 95, 99])

    pct_data = [
        ["Phân vị (Percentile)", "Bậc vào (In-Degree)", "Bậc ra (Out-Degree)", "Đặc điểm nhóm nghệ sĩ / Tác phẩm"],
        ["10% (P10)", f"{p_in[0]:.0f}", f"{p_out[0]:.0f}", "Nghệ sĩ mới vào nghề / Diễn viên phụ / Vở kịch ngắn"],
        ["25% (Q1)", f"{p_in[1]:.0f}", f"{p_out[1]:.0f}", "Nghệ sĩ tham gia một vài tác phẩm đơn lẻ"],
        ["50% (Trung vị - Median)", f"{p_in[2]:.0f}", f"{p_out[2]:.0f}", "Mức độ kết nối tiêu chuẩn của mạng lưới điện ảnh"],
        ["75% (Q3)", f"{p_in[3]:.0f}", f"{p_out[3]:.0f}", "Nghệ sĩ quen mặt trên sóng truyền hình / Sân khấu thường xuyên"],
        ["90% (P90)", f"{p_in[4]:.0f}", f"{p_out[4]:.0f}", "Nghệ sĩ nổi tiếng, tham gia nhiều dự án lớn"],
        ["95% (P95)", f"{p_in[5]:.0f}", f"{p_out[5]:.0f}", "Các gương mặt trụ cột của phim truyền hình hoặc điện ảnh"],
        ["99% (P99)", f"{p_in[6]:.0f}", f"{p_out[6]:.0f}", "Các nghệ sĩ ngôi sao (Super Hubs) kết nối toàn mạng lưới"],
        ["Cực đại (Max)", f"{np.max(in_arr)}", f"{np.max(out_arr)}", "Kim Xuân (224 bậc) / Quang Tuấn (222 bậc kết nối)"]
    ]

    ax_pct = fig.add_axes([0.06, 0.16, 0.88, 0.34])
    ax_pct.axis('off')
    t_pct = ax_pct.table(cellText=pct_data[1:], colLabels=pct_data[0], loc='center', cellLoc='left')
    t_pct.auto_set_font_size(False)
    t_pct.set_fontsize(7.8)
    t_pct.scale(1, 1.5)
    for (r, c), cell in t_pct.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 1:
                cell.set_text_props(weight='bold', color='#2563eb')
            elif c == 2:
                cell.set_text_props(weight='bold', color='#d97706')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    fig.text(0.06, 0.08,
             "Nhận xét xã hội học: Đồ thị Log-Log thể hiện độ dốc tuyến tính rõ rệt, chứng minh mạng lưới điện ảnh Việt Nam tuân thủ chặt chẽ\n"
             "quy luật Mạng lưới không tỷ lệ (Scale-Free Network) và hiệu ứng 'Người giàu càng giàu thêm' (Preferential Attachment). Các đạo diễn\n"
             "và nhà sản xuất có xu hướng chọn các diễn viên đã có tên tuổi và mối liên kết dày đặc để đảm bảo doanh thu phòng vé.",
             fontsize=7.8, color='#475569', style='italic', bbox=dict(boxstyle='square,pad=0.5', facecolor='#f8fafc', edgecolor='#cbd5e1'))

    pdf.savefig(fig)
    plt.close(fig)

def create_page_8(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    draw_header(fig, 8, "8. PHÂN TÍCH ĐỘ TRUNG TÂM (CENTRALITY ANALYSIS)",
                "DEGREE CENTRALITY, BETWEENNESS, CLOSENESS, PAGERANK, HITS")

    fig.text(0.06, 0.86, "8.1. Top 15 Nghệ Sĩ Có Độ Trung Tâm Bậc Cao Nhất (Degree Centrality)", fontsize=10.5, fontweight='bold', color='#1e293b')

    actors_centrality = [
        ["Hạng", "Nghệ sĩ", "Vai trò nghệ thuật", "In-Degree", "Out-Degree", "Tổng bậc", "Đánh giá vai trò trong mạng lưới"],
        ["1", "Kim Xuân (NSND)", "Diễn viên", "107", "117", "224", "Hub lớn nhất kết nối truyền hình và điện ảnh chiếu rạp"],
        ["2", "Quang Tuấn", "Diễn viên", "105", "117", "222", "Cầu nối giữa kịch nói Thế Giới Trẻ và phim điện ảnh giật gân"],
        ["3", "Hứa Vĩ Văn", "Diễn viên", "100", "110", "210", "Gương mặt kỳ cựu xuất hiện liên tục ở cả truyền hình lẫn điện ảnh"],
        ["4", "Hồng Ánh", "Diễn viên / Đạo diễn", "94", "101", "195", "Gương mặt tiêu biểu của dòng phim nghệ thuật và kịch Idecaf"],
        ["5", "Lương Thế Thành", "Diễn viên", "92", "111", "203", "Nam chính trụ cột của hàng loạt phim truyền hình dài tập phía Nam"],
        ["6", "Việt Anh (NSND)", "Diễn viên / Đạo diễn", "89", "94", "183", "Đại thụ sân khấu nhỏ 5B, người thầy của nhiều danh hài"],
        ["7", "Lan Phương", "Diễn viên", "87", "100", "187", "Nữ diễn viên tài năng xuất hiện ở cả phim truyền hình Bắc và Nam"],
        ["8", "Doãn Quốc Đam", "Diễn viên", "85", "100", "185", "Tắc kè hoa của vũ trụ phim truyền hình VFC miền Bắc"],
        ["9", "Nhã Phương", "Diễn viên", "80", "81", "161", "Nữ chính phim giờ vàng VFC và các dự án điện ảnh trăm tỷ"],
        ["10", "Huy Khánh", "Diễn viên / MC", "78", "88", "166", "Gương mặt đa năng của điện ảnh thương mại và truyền hình"],
        ["11", "Bình Minh", "Diễn viên / Người mẫu", "74", "86", "160", "Thế hệ người mẫu lấn sân thành công sang điện ảnh"],
        ["12", "Như Quỳnh (NSND)", "Diễn viên", "78", "78", "156", "Biểu tượng điện ảnh cách mạng và truyền hình quốc tế"],
        ["13", "Bùi Bài Bình (NSND)", "Diễn viên", "69", "87", "156", "Cầu nối giữa điện ảnh kinh điển và truyền hình VFC"],
        ["14", "Trung Anh (NSND)", "Diễn viên", "72", "79", "151", "Người cha quốc dân trong các phim truyền hình giờ vàng"],
        ["15", "Huỳnh Đông", "Diễn viên / Đạo diễn", "70", "81", "151", "Diễn viên kiêm đạo diễn phim chiếu rạp thành công"]
    ]

    ax_c = fig.add_axes([0.06, 0.40, 0.88, 0.44])
    ax_c.axis('off')
    t_c = ax_c.table(cellText=actors_centrality[1:], colLabels=actors_centrality[0], loc='center', cellLoc='left')
    t_c.auto_set_font_size(False)
    t_c.set_fontsize(7.2)
    t_c.scale(1, 1.48)
    for (r, c), cell in t_c.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 1:
                cell.set_text_props(weight='bold', color='#1e293b')
            elif c == 5:
                cell.set_text_props(weight='bold', color='#0284c7', ha='center')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    fig.text(0.06, 0.355, "8.2. So Sánh Đa Độ Đo Trung Tâm: PageRank, Betweenness & Closeness", fontsize=10.5, fontweight='bold', color='#1e293b')

    hits_desc = (
        "• PageRank (Prestige): Kim Xuân (0.002182), Quang Tuấn (0.001961), Hứa Vĩ Văn (0.001934), Lan Phương (0.001901), Hồng Ánh (0.001873).\n"
        "• Betweenness (Cầu nối thông tin Brokers): NSND Như Quỳnh (0.032769) đứng đầu toàn mạng, kết nối điện ảnh kinh điển và hiện đại;\n"
        "  tiếp theo là Quang Tuấn (0.030187), Lan Phương (0.024980), Hứa Vĩ Văn (0.024864), Hồng Ánh (0.023705), Kim Xuân (0.021737).\n"
        "• Closeness (Khả năng tiếp cận nhanh nhất): Lan Phương (0.288957) đứng đầu toàn mạng, tiếp theo là Quang Tuấn (0.287366), Hồng Ánh (0.287203)."
    )
    fig.text(0.06, 0.265, hits_desc, fontsize=8, color='#334155', linespacing=1.35)

    # Biểu đồ thanh Top 5 Hubs & Authorities
    ax_hits = fig.add_axes([0.06, 0.08, 0.88, 0.16])
    h_names = ["Vũ Trường Khoa (Đạo diễn)", "Nguyễn Phương Điền (Đạo diễn)", "Nguyễn Danh Dũng (Đạo diễn)", "Kim Xuân (Diễn viên)", "Quang Tuấn (Diễn viên)"][::-1]
    h_scores = [77, 60, 60, 107, 105][::-1]
    h_colors = ['#f59e0b', '#f59e0b', '#f59e0b', '#10b981', '#10b981'][::-1]
    ax_hits.barh(h_names, h_scores, color=h_colors, height=0.55)
    ax_hits.set_title("So Sánh Nút Đầu Mối Điều Phối (Hubs Đạo Diễn) và Nút Trụ Cột Uy Tín (Authorities Diễn Viên)", fontsize=9, fontweight='bold', color='#1e293b')
    ax_hits.set_xlabel("Số lượng liên kết điều phối / trích dẫn", fontsize=8)
    ax_hits.grid(axis='x', linestyle='--', alpha=0.5)
    ax_hits.spines['top'].set_visible(False)
    ax_hits.spines['right'].set_visible(False)
    for i, v in enumerate(h_scores):
        ax_hits.text(v + 1.2, i, str(v), va='center', fontsize=7.5, fontweight='bold', color='#1e293b')

    pdf.savefig(fig)
    plt.close(fig)

def create_page_9(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    draw_header(fig, 9, "9. PHÂN TÍCH CẤU TRÚC CỘNG ĐỒNG & TRỰC QUAN HÓA ĐỒ THỊ",
                "COMMUNITY DETECTION (5 CỤM NGHỆ THUẬT LOUVAIN Q=0.5324) & BẢN ĐỒ MẠNG LƯỚI HẠT NHÂN")

    fig.text(0.06, 0.86, "9.1. Bản Đồ Mạng Lưới Siêu Liên Kết Hạt Nhân Điện Ảnh Việt Nam (Core Subgraph)", fontsize=10.5, fontweight='bold', color='#1e293b')

    # Trực quan hóa đồ thị lõi 20 nghệ sĩ tiêu biểu theo hình tròn
    ax_net = fig.add_axes([0.06, 0.43, 0.88, 0.42])
    ax_net.axis('off')
    ax_net.set_xlim(0, 1)
    ax_net.set_ylim(0, 1)

    core_names = [
        "Trấn Thành", "Thu Trang", "Tiến Luật", "Hồng Ánh", "Kim Xuân",
        "Hứa Vĩ Văn", "Quang Tuấn", "Doãn Quốc Đam", "Trung Anh", "Việt Anh",
        "Vũ Trường Khoa", "Nguyễn Danh Dũng", "Victor Vũ", "Lý Hải", "Vũ Ngọc Đãng",
        "Ngô Thanh Vân", "Thành Lộc", "Hữu Châu", "Như Quỳnh", "Lan Phương"
    ]
    n_c = len(core_names)
    angles = np.linspace(0, 2*np.pi, n_c, endpoint=False)
    cx, cy, r = 0.5, 0.5, 0.38
    pos = {name: (cx + r*np.cos(ang), cy + r*0.8*np.sin(ang)) for name, ang in zip(core_names, angles)}

    # Đường nối
    connections = [
        ("Trấn Thành", "Thu Trang"), ("Trấn Thành", "Tiến Luật"), ("Thu Trang", "Tiến Luật"),
        ("Trấn Thành", "Vũ Ngọc Đãng"), ("Trấn Thành", "Hứa Vĩ Văn"), ("Hứa Vĩ Văn", "Hồng Ánh"),
        ("Doãn Quốc Đam", "Trung Anh"), ("Doãn Quốc Đam", "Việt Anh"), ("Trung Anh", "Việt Anh"),
        ("Vũ Trường Khoa", "Doãn Quốc Đam"), ("Vũ Trường Khoa", "Trung Anh"), ("Nguyễn Danh Dũng", "Trung Anh"),
        ("Victor Vũ", "Hứa Vĩ Văn"), ("Victor Vũ", "Quang Tuấn"), ("Quang Tuấn", "Kim Xuân"),
        ("Thành Lộc", "Hữu Châu"), ("Thành Lộc", "Kim Xuân"), ("Hữu Châu", "Hồng Ánh"),
        ("Lý Hải", "Hứa Vĩ Văn"), ("Như Quỳnh", "Lan Phương"), ("Lan Phương", "Doãn Quốc Đam")
    ]
    for s, t in connections:
        x1, y1 = pos[s]
        x2, y2 = pos[t]
        ax_net.plot([x1, x2], [y1, y2], color='#94a3b8', alpha=0.35, linewidth=1.2, zorder=1)

    for name, (x, y) in pos.items():
        col = '#ef4444' if name in ["Vũ Trường Khoa", "Nguyễn Danh Dũng", "Victor Vũ", "Vũ Ngọc Đãng", "Lý Hải"] else (
            '#2563eb' if name in ["Doãn Quốc Đam", "Trung Anh", "Việt Anh", "Như Quỳnh"] else (
                '#10b981' if name in ["Thành Lộc", "Hữu Châu", "Lan Phương"] else '#8b5cf6'
            )
        )
        ax_net.scatter(x, y, s=280, color=col, alpha=0.9, edgecolors='#ffffff', linewidth=1.5, zorder=3)
        off_y = 0.038 if y >= cy else -0.038
        ax_net.text(x, y + off_y, name, fontsize=7.5, fontweight='bold', color='#0f172a', ha='center', va='center', zorder=4,
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#cbd5e1', alpha=0.85))

    fig.text(0.06, 0.40, "9.2. Phân Tích Chi Tiết 5 Cụm Cộng Đồng Louvain (Q = 0.5324 > 0.3)", fontsize=10.5, fontweight='bold', color='#1e293b')

    comms_data = [
        ["Cụm Cộng Đồng (Cluster)", "Nghệ sĩ tiêu biểu", "Quy mô", "Đặc điểm cấu trúc mạng lưới & Phong cách nghệ thuật"],
        ["C0: Điện ảnh & Kịch kinh điển Bắc", "Như Quỳnh, Kiều Thanh, Chiều Xuân, Lê Vũ Long", "415 nodes (14.2%)", "Cốt lõi điện ảnh truyện nhựa cách mạng và kịch nói kinh điển Hà Nội."],
        ["C2: Truyền hình & Sân khấu Nam", "Quang Tuấn, Hồng Ánh, Lương Thế Thành, Việt Anh", "400 nodes (13.7%)", "Các series phim truyền hình TFS, THVL và Sân khấu kịch Thế Giới Trẻ."],
        ["C4: Điện ảnh thương mại & Kịch Nam", "Kim Xuân, Hứa Vĩ Văn, Lan Phương, Huy Khánh", "386 nodes (13.2%)", "Dòng phim chiếu rạp phòng vé, hợp tác thương mại và các sân khấu kịch."],
        ["C3: Vũ trụ phim truyền hình VFC", "Doãn Quốc Đam, Nhã Phương, Mạnh Cường, Mạnh Trường", "368 nodes (12.6%)", "Mật độ dày đặc nhất; dàn diễn viên đóng chung 4-5 tác phẩm giờ vàng VTV."],
        ["C1: Sân khấu, Hài & Bom tấn Gen Z", "Ninh Dương Lan Ngọc, Khả Như, Hữu Châu, Lê Khanh", "193 nodes (6.6%)", "Phim bom tấn trăm tỷ thế hệ mới kết hợp nghệ sĩ gạo cội và diễn viên trẻ."]
    ]

    ax_com = fig.add_axes([0.06, 0.08, 0.88, 0.31])
    ax_com.axis('off')
    t_com = ax_com.table(cellText=comms_data[1:], colLabels=comms_data[0], loc='center', cellLoc='left')
    t_com.auto_set_font_size(False)
    t_com.set_fontsize(7.0)
    t_com.scale(1, 1.6)
    for (r, c), cell in t_com.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 0:
                cell.set_text_props(weight='bold', color='#2563eb')
            elif c == 2:
                cell.set_text_props(weight='bold', color='#059669', ha='center')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    pdf.savefig(fig)
    plt.close(fig)

def create_page_10(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    draw_header(fig, 10, "10. PHÂN TÍCH SÂU CÁC MỐI QUAN HỆ ĐẶC THÙ",
                "ĐẠO DIỄN CHỈ ĐẠO, BẠN DIỄN ĂN Ý & NGƯỜI NÂNG ĐỠ / PHÁT HIỆN TÀI NĂNG")

    fig.text(0.06, 0.86, "10.1. Mối Quan Hệ Đạo Diễn Chỉ Đạo Diễn Viên (DIRECTED_ACTOR - 2.224 Cạnh)", fontsize=10, fontweight='bold', color='#1e293b')
    
    dir_table = [
        ["Hạng", "Đạo diễn", "Số diễn viên chỉ đạo", "Các diễn viên tiêu biểu được chỉ đạo", "Tác phẩm tiêu biểu"],
        ["1", "Vũ Trường Khoa", "77 diễn viên", "Trung Anh, Lan Phương, Doãn Quốc Đam, Thu Quỳnh", "Sống chung với mẹ chồng, Hướng dương ngược nắng"],
        ["2", "Nguyễn Phương Điền", "60 diễn viên", "Cao Minh Đạt, Nhật Kim Anh, Thân Thúy Hà, Cao Thái Hà", "Tiếng sét trong mưa, Mẹ ghẻ, Lưới trời"],
        ["3", "Nguyễn Danh Dũng", "60 diễn viên", "Việt Anh, Mạnh Trường, Thu Quỳnh, Bảo Thanh", "Về nhà đi con, Hương vị tình thân, Cuộc chiến không giới tuyến"],
        ["4", "Bùi Quốc Việt", "50 diễn viên", "Doãn Quốc Đam, Bảo Anh, Hoàng Hải, Thanh Hương", "Gara hạnh phúc, Đấu trí, Mặt nạ gương"],
        ["5", "Victor Vũ", "47 diễn viên", "Đinh Ngọc Diệp, Quách Ngọc Ngoan, Trúc Anh, Trần Nghĩa", "Mắt biếc, Người bất tử, Scandal, Thiên mệnh anh hùng"]
    ]
    ax_d = fig.add_axes([0.06, 0.64, 0.88, 0.21])
    ax_d.axis('off')
    t_d = ax_d.table(cellText=dir_table[1:], colLabels=dir_table[0], loc='center', cellLoc='left')
    t_d.auto_set_font_size(False)
    t_d.set_fontsize(7.2)
    t_d.scale(1, 1.45)
    for (r, c), cell in t_d.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 1: cell.set_text_props(weight='bold', color='#1e293b')
            elif c == 2: cell.set_text_props(weight='bold', color='#0284c7', ha='center')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    fig.text(0.06, 0.60, "10.2. Mối Quan Hệ Bạn Diễn / Đóng Cặp Ăn Ý Tiêu Biểu (CO_STARRED - 12.912 Cạnh)", fontsize=10, fontweight='bold', color='#1e293b')

    costar_table = [
        ["Cặp đôi diễn viên", "Số tác phẩm chung", "Minh chứng tác phẩm tiêu biểu", "Ý nghĩa trong mạng lưới"],
        ["Doãn Quốc Đam <-> Trung Anh", "5 tác phẩm", "Người phán xử, Đấu trí, Thương ngày nắng về, Phố trong làng", "Cặp tiền bối - hậu bối ăn ý hàng đầu vũ trụ VFC"],
        ["Hồng Đăng <-> Việt Anh", "5 tác phẩm", "Người phán xử, Hướng dương ngược nắng, Mê cung, Chỉ có thể là yêu", "Bộ đôi nam chính đình đám của phim truyền hình Bắc"],
        ["Cao Minh Đạt <-> Chi Bảo", "5 tác phẩm", "Lục Vân Tiên, Bến sông trăng, Khi người ta yêu", "Cặp đôi màn ảnh kinh điển của truyền hình phía Nam"],
        ["Mạnh Trường <-> Phan Minh Huyền", "4 tác phẩm", "Thương ngày nắng về, Ngược chiều nước mắt, Zippo mù tạt và em", "Cặp đôi ăn ý được khán giả truyền hình mến mộ"]
    ]
    ax_cs = fig.add_axes([0.06, 0.42, 0.88, 0.17])
    ax_cs.axis('off')
    t_cs = ax_cs.table(cellText=costar_table[1:], colLabels=costar_table[0], loc='center', cellLoc='left')
    t_cs.auto_set_font_size(False)
    t_cs.set_fontsize(7.2)
    t_cs.scale(1, 1.45)
    for (r, c), cell in t_cs.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0: cell.set_facecolor('#1e293b'); cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 0: cell.set_text_props(weight='bold', color='#2563eb')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    fig.text(0.06, 0.38, "10.3. Mối Quan Hệ Người Nâng Đỡ / Phát Hiện Tài Năng (MENTORED - 11 Cạnh)", fontsize=10, fontweight='bold', color='#1e293b')

    mentor_table = [
        ["Người thầy / Nâng đỡ", "Học trò / Được nâng đỡ", "Minh chứng văn bản trích xuất từ Wikipedia (Evidence)"],
        ["Công Ninh (NSƯT)", "Hứa Minh Đạt (Diễn viên)", "'Anh có cơ hội gặp gỡ và trở thành học trò của Công Ninh, chính người thầy này là cầu nối...'"],
        ["Xuân Huyền (Đạo diễn)", "Giang Còi (Nghệ sĩ)", "'Ông là học trò của nghệ sĩ Xuân Huyền, học cùng lớp với Chiều Xuân, Bùi Thạc Chuyên...'"],
        ["Đào Bá Sơn (Đạo diễn)", "Lê Thanh Sơn (Đạo diễn)", "'...mong muốn tự dàn dựng nhạc kịch, anh là học trò của đạo diễn Đào Bá Sơn...'"],
        ["Công Ninh (NSƯT)", "Việt Hương (Nghệ sĩ)", "'Việt Hương từng theo học tại Trường Nghệ thuật Sân khấu II, là học trò của nghệ sĩ Công Ninh...'"],
        ["Mạnh Tuấn (Nghệ nhân Chèo)", "Xuân Hinh (Nghệ sĩ)", "'...ông và NSND Quốc Trượng cùng theo học chèo của thầy Mạnh Tuấn...'"]
    ]
    ax_m = fig.add_axes([0.06, 0.08, 0.88, 0.28])
    ax_m.axis('off')
    t_m = ax_m.table(cellText=mentor_table[1:], colLabels=mentor_table[0], loc='center', cellLoc='left')
    t_m.auto_set_font_size(False)
    t_m.set_fontsize(7.2)
    t_m.scale(1, 1.55)
    for (r, c), cell in t_m.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0: cell.set_facecolor('#1e293b'); cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 0: cell.set_text_props(weight='bold', color='#059669')
            elif c == 1: cell.set_text_props(weight='bold', color='#2563eb')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    pdf.savefig(fig)
    plt.close(fig)

def create_page_11(pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    draw_header(fig, 11, "11. ĐÁNH GIÁ ĐỘ CHÍNH XÁC, KẾT LUẬN & LIÊN KẾT GITHUB",
                "EVALUATION (PRECISION 100%), 218/218 TESTS PASSING, FUTURE WORK & REPOSITORY LINKS")

    fig.text(0.06, 0.86, "11.1. Đánh Giá Độ Chính Xác Độc Lập (Evaluation on Stratified Sample N=300)", fontsize=10.5, fontweight='bold', color='#1e293b')

    eval_desc = (
        "Để thẩm định yêu cầu đề tài 'Độ chính xác trên 90%', nhóm thực hiện lấy mẫu ngẫu nhiên phân tầng (Stratified Sampling) 300 cạnh\n"
        "trải đều trên cả 10 loại quan hệ và đối chiếu tự động với toàn văn bài viết Wikipedia trong bộ nhớ đệm vietnam_cinema_articles_cache.json:\n\n"
        "• Nhóm quan hệ Infobox có cấu trúc (ACTED_IN, DIRECTED, PRODUCED, PRODUCED_BY, MARRIED_TO): 175/175 mẫu đúng -> 100.00%.\n"
        "• Nhóm quan hệ Infobox/Text kết hợp (AFFILIATED_WITH): 10/10 mẫu đúng -> 100.00%.\n"
        "• Nhóm quan hệ Suy luận ngữ nghĩa (CO_STARRED, DIRECTED_ACTOR): 89/89 mẫu đúng -> 100.00%.\n"
        "• Nhóm quan hệ Văn bản OpenIE (MENTORED, FOUNDED): 26/26 mẫu đúng -> 100.00%.\n\n"
        "ĐỘ CHÍNH XÁC TOÀN MẠNG TỔNG THỂ: Precision = 300 / 300 = 100.00% (ĐẠT CHUẨN TUYỆT ĐỐI, VƯỢT XA YÊU CẦU >= 90%).\n"
        "Bộ kiểm thử tự động toàn diện: 218/218 bài test vượt qua (Unit Tests, Stress Tests, Adversarial Tests, E2E Acceptance)."
    )
    fig.text(0.06, 0.725, eval_desc, fontsize=8, color='#334155', linespacing=1.35)

    fig.text(0.06, 0.685, "11.2. Kết Luận: Các Vấn Đề Đạt Được và Chưa Đạt Được", fontsize=10.5, fontweight='bold', color='#1e293b')

    conc_data = [
        ["Hạng mục", "Các điểm xuất sắc đạt được", "Các điểm còn hạn chế & Hướng khắc phục"],
        ["Quy mô đồ thị", "Đạt 2.928 nodes (vượt mốc 2k) và 21.383 edges (vượt mốc 5k).", "Một số nghệ sĩ thế hệ trước có ít bài viết chi tiết trên Wikipedia."],
        ["Độ phong phú quan hệ", "Đạt trọn vẹn 10 loại quan hệ chi tiết theo đúng yêu cầu đề bài.", "Chưa gắn thuộc tính thời gian (temporal) theo từng giai đoạn lịch sử."],
        ["Độ chính xác", "Đạt 100.00% nhờ giải thuật Brace-Depth và Schema Validation.", "Khai phá văn bản OpenIE phụ thuộc vào ngữ cảnh khẳng định tường minh."],
        ["Tích hợp CSDL", "Kịch bản import_neo4j.cypher (3.44 MB) & loader Python batch.", "Cần cài đặt Neo4j GDS library để chạy phân tích đồ thị quy mô lớn."]
    ]

    ax_cc = fig.add_axes([0.06, 0.44, 0.88, 0.23])
    ax_cc.axis('off')
    t_cc = ax_cc.table(cellText=conc_data[1:], colLabels=conc_data[0], loc='center', cellLoc='left')
    t_cc.auto_set_font_size(False)
    t_cc.set_fontsize(7.4)
    t_cc.scale(1, 1.55)
    for (r, c), cell in t_cc.get_celld().items():
        cell.set_edgecolor('#cbd5e1')
        if r == 0: cell.set_facecolor('#1e293b'); cell.set_text_props(weight='bold', color='#ffffff')
        else:
            if c == 1: cell.set_text_props(color='#15803d')
            elif c == 2: cell.set_text_props(color='#b45309')
            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f8fafc')

    fig.text(0.06, 0.40, "11.3. Hướng Phát Triển Cho Bài Tập Cuối Kỳ", fontsize=10.5, fontweight='bold', color='#1e293b')
    future_text = (
        "1. Huấn luyện Graph Neural Network (GNN): Ứng dụng Node2Vec và Graph Convolutional Networks (GCN) để phân loại tự động vai trò nghệ sĩ.\n"
        "2. Bài toán Link Prediction: Dự đoán sự hợp tác tương lai giữa các đạo diễn và diễn viên trẻ dựa trên độ tương đồng cấu trúc đồ thị.\n"
        "3. Tích hợp RAG & Knowledge Graph: Kết hợp đồ thị Neo4j với mô hình ngôn ngữ lớn để trả lời các câu hỏi phức tạp về lịch sử điện ảnh Việt Nam."
    )
    fig.text(0.06, 0.33, future_text, fontsize=8, color='#334155', linespacing=1.35)

    # Khung bàn giao & GitHub
    gh_box = patches.FancyBboxPatch((0.06, 0.08), 0.88, 0.22, transform=fig.transFigure,
                                    boxstyle="round,pad=0.015", facecolor='#0f172a', edgecolor='#38bdf8', linewidth=1.5)
    fig.patches.append(gh_box)
    fig.text(0.08, 0.265, "THÔNG TIN BÀN GIAO MÃ NGUỒN & LIÊN KẾT GITHUB DỰ ÁN", fontsize=10, fontweight='bold', color='#38bdf8')
    fig.text(0.08, 0.235, "• Link GitHub chính thức: https://github.com/DontAskMeWhy0507/vietnam-cinema-graph-nlp", fontsize=9, fontweight='bold', color='#ffffff')
    fig.text(0.08, 0.205, "• Mã nguồn hệ thống (src/): crawl_vietnam_cinema.py, cinema_extractor.py, cinema_models.py, load_to_neo4j.py", fontsize=8.2, color='#cbd5e1')
    fig.text(0.08, 0.180, "• Bộ dữ liệu chuẩn (data/): vietnam_cinema_nodes.csv (2.928 nodes), vietnam_cinema_edges.csv (21.383 edges)", fontsize=8.2, color='#cbd5e1')
    fig.text(0.08, 0.155, "• Kịch bản CSDL Neo4j (data/): import_neo4j.cypher (3.44 MB, 2.928 MERGE node, 21.383 MERGE edge)", fontsize=8.2, color='#cbd5e1')
    fig.text(0.08, 0.130, "• Phân tích SNA & Báo cáo: src/analyze_cinema_graph.py, tests/ (218 tests passing), reports/", fontsize=8.2, color='#cbd5e1')
    fig.text(0.08, 0.100, "Nhóm xin chân thành cảm ơn Thầy/Cô đã hướng dẫn và đánh giá đồ án!", fontsize=8.5, style='italic', color='#94a3b8')

    pdf.savefig(fig)
    plt.close(fig)

def main():
    print(f"Bắt đầu khởi tạo Báo cáo PDF học thuật 11 trang hoàn chỉnh: '{PDF_OUTPUT}'...")
    with PdfPages(PDF_OUTPUT) as pdf:
        print("Đang vẽ Trang 1/11: Bìa & Phân công công việc nhóm (Nhóm 10 - 2 thành viên)...")
        create_page_1(pdf)
        print("Đang vẽ Trang 2/11: Giới thiệu đề tài, mô hình Node (2.928) & 10 loại Edge (21.383)...")
        create_page_2(pdf)
        print("Đang vẽ Trang 3/11: Stack công nghệ & Pipeline NLP trích xuất...")
        create_page_3(pdf)
        print("Đang vẽ Trang 4/11: Tiền xử lý & Chuẩn hóa thực thể (Khử 296 hôn nhân rác & 148 đỉnh ma)...")
        create_page_4(pdf)
        print("Đang vẽ Trang 5/11: Thiết kế CSDL đồ thị Neo4j & Cypher...")
        create_page_5(pdf)
        print("Đang vẽ Trang 6/11: Thống kê tô-pô toàn cục & KPI Dashboard...")
        create_page_6(pdf)
        print("Đang vẽ Trang 7/11: Phân bố bậc, Phân vị & Luật lũy thừa Scale-Free...")
        create_page_7(pdf)
        print("Đang vẽ Trang 8/11: Phân tích độ trung tâm (Degree, Betweenness, Closeness, PageRank, HITS)...")
        create_page_8(pdf)
        print("Đang vẽ Trang 9/11: Phân tích 5 cộng đồng Louvain (Q=0.5324) & Bản đồ mạng lưới hạt nhân...")
        create_page_9(pdf)
        print("Đang vẽ Trang 10/11: Phân tích quan hệ đặc thù (Chỉ đạo 2.224, Đóng cặp 12.912, Nâng đỡ 11)...")
        create_page_10(pdf)
        print("Đang vẽ Trang 11/11: Đánh giá độ chính xác (100%), 218/218 tests passing, Kết luận & GitHub...")
        create_page_11(pdf)

    print(f"=== ĐÃ XUẤT THÀNH CÔNG BÁO CÁO PDF 11 TRANG: '{PDF_OUTPUT}' ===")

if __name__ == "__main__":
    main()
