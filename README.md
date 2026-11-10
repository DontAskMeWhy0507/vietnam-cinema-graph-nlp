# Mạng Lưới Xã Hội Điện Ảnh & Sân Khấu Việt Nam (Vietnam Cinema SNA)
> **BÀI TẬP LỚN: XÂY DỰNG MẠNG XÃ HỘI DỰA TRÊN KỸ THUẬT PHÂN TÍCH XỬ LÝ NGÔN NGỮ TỰ NHIÊN (NLP)**
> 
> **Khai thác Infobox và Văn bản Wikipedia tiếng Việt để Trích xuất Mạng Tri thức Điện ảnh & Sân khấu**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Graph%20DB-Neo4j%205.x-green.svg)](https://neo4j.com/)
[![Nodes](https://img.shields.io/badge/Nodes-2%2C928-orange.svg)]()
[![Edges](https://img.shields.io/badge/Edges-21%2C383-red.svg)]()
[![Modularity](https://img.shields.io/badge/Louvain%20Q-0.5324-blueviolet.svg)]()
[![Precision](https://img.shields.io/badge/Precision-100.00%25-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Tests-218%2F218%20Passing-success.svg)]()
[![Report](https://img.shields.io/badge/Report-11%20Pages%20PDF-purple.svg)](./reports/BAO_CAO_BAI_TAP_LON_SNA.pdf)

---

## 1. Giới Thiệu Đề Tài

Dự án thực hiện thu thập, trích xuất thực thể và liên kết quan hệ tự động từ **2.253 bài viết Wikipedia tiếng Việt & Anh** thuộc chủ đề điện ảnh, sân khấu, diễn viên, đạo diễn và tác phẩm nghệ thuật Việt Nam.

Hệ thống kết hợp **Regex Template Engine** phân tích Infobox chuẩn hóa với mô hình **Open Information Extraction (Open IE)** đọc hiểu văn bản tự nhiên tại các mục *"Tiểu sử"*, *"Sự nghiệp điện ảnh"*, *"Sân khấu"*. Dữ liệu sau đó trải qua quy trình khử nhiễu sâu (loại bỏ 296 hôn nhân rác và 148 đỉnh ma), tạo nên một đồ thị mạng xã hội tri thức hoàn chỉnh gồm **2.928 đỉnh** và **21.383 cạnh có hướng**, sẵn sàng nạp trực tiếp vào hệ quản trị cơ sở dữ liệu đồ thị **Neo4j 5.x**.

### 1.1. Phân Công Công Việc Trong Nhóm (Nhóm 10 - 2 Thành Viên)

| STT | Thành viên | Vai trò | Trách nhiệm chính | Tỷ lệ |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Vũ Tiến Tuấn Trung** *(Trưởng nhóm)*<br>`MSSV: 23020576` | **Data Collection, NLP Extraction Pipeline & System Architecture** | Khảo sát cấu trúc chuyên mục Wikipedia, thiết kế crawler bất đồng bộ `src/crawl_vietnam_cinema.py`, bóc tách Infobox với giải thuật Brace-Depth Tracking, regex OpenIE trích xuất văn bản Sự nghiệp/Tiểu sử và bộ nhớ đệm 2.253 bài. | 100% |
| 2 | **Đặng Anh Quế**<br>`MSSV: 23020565` | **Graph Modeling, Neo4j, SNA Analytics & Academic Reporting** | Thiết kế Ontology HIN 2.928 đỉnh, mô hình hóa CSDL đồ thị Neo4j 5.x, sinh kịch bản `data/import_neo4j.cypher` (3.44 MB) và `src/load_to_neo4j.py`, lập trình thuật toán SNA (Degree, Betweenness, Closeness, Louvain Q=0.5324), kịch bản kiểm định độc lập N=300 mẫu, 218 unit tests và xuất bản báo cáo PDF 11 trang + Markdown. | 100% |

---

## 2. Bảng Tổng Hợp Chỉ Số Đạt Được

| Tiêu chuẩn yêu cầu bài tập | Mức tối thiểu yêu cầu | Thực tế đạt được | Đánh giá |
| :--- | :---: | :---: | :---: |
| **Quy mô số đỉnh (Nodes)** | $\ge$ 2.000 nút (hoặc 1.000) | **2.928 Đỉnh** *(Person: 1.899, Artwork: 913, Organization: 116)* | **Vượt 146.4%** |
| **Quy mô số cạnh (Edges)** | $\ge$ 5.000 cạnh | **21.383 Cạnh có hướng** | **Vượt 427.7%** |
| **Số loại quan hệ ngữ nghĩa** | $\ge$ 10 loại quan hệ | **Đúng 10 loại quan hệ chi tiết** | **Đạt 10/10** |
| **Độ chính xác mạng lưới** | $\ge$ 90% | **100.00%** *(Thẩm định độc lập 300 cạnh mẫu)* | **Đạt chuẩn tuyệt đối** |
| **Hệ số phân cụm Louvain** | $Q > 0.3$ | **$Q = 0.5324$** *(5 cộng đồng nghệ thuật lớn)* | **Phân cụm rất mạnh** |
| **Bộ kiểm thử tự động** | Vượt qua 100% | **218 / 218 Tests Passing** | **Hoàn thành** |
| **Hệ quản trị CSDL Graph** | Neo4j / ArangoDB,... | **Neo4j 5.x** *(kèm script Cypher 3.44 MB & Python loader)* | **Hoàn thành** |
| **Báo cáo học thuật** | $\ge$ 10 trang | **11 Trang PDF A4 màu** + file Markdown $\ge 750$ dòng | **Vượt chỉ tiêu** |

---

## 3. Thống Kê 10 Loại Quan Hệ Chi Tiết (10 Edge Relationship Types)

Mạng lưới tuân thủ nghiêm ngặt ràng buộc bản thể học (Ontology Constraints):

| STT | Mã quan hệ (`rel_type`) | Đỉnh nguồn $\to$ Đích | Số lượng cạnh | Tỷ lệ (%) | Định nghĩa & Ý nghĩa nghiệp vụ |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | `CO_STARRED` | Person $\leftrightarrow$ Person | **12.912** | **60.38%** | Diễn viên đóng cặp / hợp tác trong cùng tác phẩm |
| **2** | `ACTED_IN` | Person $\to$ Artwork | **4.761** | **22.27%** | Diễn viên tham gia diễn xuất trong phim / kịch |
| **3** | `DIRECTED_ACTOR` | Person $\to$ Person | **2.224** | **10.40%** | Đạo diễn chỉ đạo diễn xuất diễn viên trong phim |
| **4** | `DIRECTED` | Person $\to$ Artwork | **711** | **3.33%** | Đạo diễn chỉ đạo sản xuất tác phẩm nghệ thuật |
| **5** | `PRODUCED_BY` | Artwork $\to$ Organization | **345** | **1.61%** | Phim được sản xuất bởi hãng phim / đài TH |
| **6** | `MARRIED_TO` | Person $\leftrightarrow$ Person | **200** | **0.94%** | Quan hệ hôn nhân / bạn đời nghệ sĩ ngoài đời thực |
| **7** | `PRODUCED` | Person $\to$ Artwork | **136** | **0.64%** | Nhà sản xuất (Producer) đầu tư sản xuất phim |
| **8** | `AFFILIATED_WITH` | Person $\to$ Organization | **67** | **0.31%** | Nghệ sĩ công tác / biên chế tại Nhà hát, Đoàn kịch |
| **9** | `FOUNDED` | Person $\to$ Organization | **16** | **0.07%** | Nghệ sĩ sáng lập sân khấu, hãng phim, nhóm kịch |
| **10**| `MENTORED` | Person $\to$ Person | **11** | **0.05%** | Thầy trò nghệ thuật, người nâng đỡ, phát hiện tài năng |
| **Tổng** | **10 Loại quan hệ** | — | **21.383** | **100.00%** | **Đầy đủ 10/10 quan hệ đặc thù** |

---

## 4. Cấu Trúc Thư Mục Dự Án

```
├── README.md                      # Tài liệu tổng quan & hướng dẫn dự án
├── requirements.txt               # Danh sách thư viện Python phụ thuộc
├── PROJECT.md                     # Bản thiết kế kiến trúc và lộ trình hoàn thiện
│
├── data/                          # Dữ liệu đồ thị và kịch bản Neo4j
│   ├── vietnam_cinema_nodes.csv   # Danh sách 2.928 đỉnh (Person, Artwork, Organization)
│   ├── vietnam_cinema_edges.csv   # Danh sách 21.383 cạnh có hướng & minh chứng văn bản
│   └── import_neo4j.cypher        # Kịch bản 3.44 MB nạp CSDL đồ thị Neo4j
│
├── src/                           # Toàn bộ mã nguồn thu thập, trích xuất & phân tích
│   ├── crawl_vietnam_cinema.py    # Pipeline thu thập dữ liệu Wikipedia & trích xuất đồ thị
│   ├── cinema_extractor.py        # Module NLP (Regex Infobox + Rule-based Open IE)
│   ├── cinema_models.py           # Mô hình dữ liệu Graph, Node, Edge & CSV/Cypher Exporter
│   ├── analyze_cinema_graph.py    # Script tính toán SNA (Degree, Betweenness, Closeness, Louvain)
│   ├── load_to_neo4j.py           # Script nạp CSDL Neo4j bằng Python official driver
│   └── generate_cinema_report_pdf.py # Script biên soạn & xuất báo cáo PDF 11 trang đồ họa cao
│
├── tests/                         # Bộ kiểm thử tự động toàn diện (218 test cases)
│   ├── test_challenger_adversarial.py   # Test trường hợp biên và dữ liệu thù địch
│   ├── test_challenger_m1m2_deep_audit.py # Test chất lượng sâu và tính toàn vẹn Cypher
│   ├── test_challenger_sna_stress.py    # Test độ chịu tải các giải thuật SNA
│   ├── test_cinema_models.py      # Unit test kiểm thử cấu trúc dữ liệu đồ thị
│   ├── test_cinema_extractor.py   # Unit test kiểm thử bộ trích xuất NLP
│   ├── test_sna_metrics.py        # Unit test các độ đo tô-pô mạng
│   ├── test_e2e_acceptance.py     # E2E acceptance test 4 tầng (115 tests)
│   └── verify_precision.py        # Script kiểm định độc lập độ chính xác trên 300 mẫu
│
├── vietnam_cinema_articles_cache.json # Bộ nhớ đệm 2.253 bài viết wikitext (38.4 MB)
│
└── reports/                       # Báo cáo học thuật hoàn chỉnh
    ├── BAO_CAO_BAI_TAP_LON_SNA.pdf # Báo cáo PDF 11 trang A4 màu chuẩn in ấn
    ├── BAO_CAO_BAI_TAP_LON_SNA.md # Toàn văn báo cáo học thuật định dạng Markdown (>= 750 dòng)
    └── precision_evaluation.json  # Bản ghi chi tiết 300 mẫu kiểm định độ chính xác 100%
```

---

## 5. Hướng Dẫn Cài Đặt & Tái Hiện (Quick Start)

### 5.1. Yêu cầu môi trường
- Python 3.10 hoặc 3.11
- Git
- Neo4j Desktop 5.x hoặc Neo4j Community Server (tùy chọn để trực quan hóa CSDL)

### 5.2. Cài đặt thư viện phụ thuộc
```bash
git clone https://github.com/DontAskMeWhy0507/vietnam-cinema-graph-nlp.git
cd vietnam-cinema-graph-nlp
pip install -r requirements.txt
```

### 5.3. Chạy kiểm thử tự động & Thẩm định độ chính xác
```bash
# 1. Chạy toàn bộ 218 tests tự động
pytest tests/ -v

# 2. Chạy kịch bản thẩm định độ chính xác độc lập trên 300 mẫu phân tầng
python tests/verify_precision.py
```

### 5.4. Thu thập & Trích xuất đồ thị (Tùy chọn chạy lại từ cache)
```bash
python src/crawl_vietnam_cinema.py
```
*Kết quả xuất tự động vào thư mục `data/`: `vietnam_cinema_nodes.csv`, `vietnam_cinema_edges.csv`, và `import_neo4j.cypher`.*

### 5.5. Phân tích mạng lưới xã hội (SNA Analysis)
```bash
python src/analyze_cinema_graph.py
```
*Tính toán: Degree Centrality, In/Out-degree, PageRank, HITS Authority/Hub, Louvain Communities ($Q=0.5324$), Betweenness Brokers, Closeness Reachability, Reciprocity, SCC/WCC.*

### 5.6. Xuất báo cáo PDF 11 trang
```bash
python src/generate_cinema_report_pdf.py
```
*Tạo file `reports/BAO_CAO_BAI_TAP_LON_SNA.pdf` chuẩn đồ họa in ấn.*

---

## 6. Hướng Dẫn Nạp Dữ Liệu Vào Neo4j

### Cách 1: Nạp trực tiếp bằng Cypher-shell
```bash
cypher-shell -u neo4j -p <password> -f data/import_neo4j.cypher
```

### Cách 2: Nạp tự động qua Python Batch Loader (`src/load_to_neo4j.py`)
```bash
# Nạp với cổng mặc định bolt://localhost:7687:
python src/load_to_neo4j.py --uri bolt://localhost:7687 --user neo4j --password <password>

# Tùy chọn xóa dữ liệu cũ trước khi nạp:
python src/load_to_neo4j.py --uri bolt://localhost:7687 --user neo4j --password <password> --wipe
```

### Cách 3: Truy vấn trực quan hóa các quan hệ đặc thù trên Neo4j Browser
```cypher
// 1. Xem mạng lưới Thầy trò nâng đỡ (MENTORED)
MATCH (mentor:Person)-[r:MENTORED]->(mentee:Person)
RETURN mentor.name AS NguoiThay, mentee.name AS HocTro, r.evidence AS MinhChung;

// 2. Xem đạo diễn chỉ đạo nhiều diễn viên nhất (DIRECTED_ACTOR)
MATCH (d:Person)-[r:DIRECTED_ACTOR]->(a:Person)
RETURN d.name AS DaoDien, a.name AS DienVien, count(r) AS SoLanHopTac
ORDER BY SoLanHopTac DESC LIMIT 15;

// 3. Xem cặp đôi diễn viên đóng cặp ăn ý nhất (CO_STARRED)
MATCH (a1:Person)-[r:CO_STARRED]->(a2:Person)
WHERE id(a1) < id(a2)
RETURN a1.name AS DienVien1, a2.name AS DienVien2, count(r) AS SoPhimChung
ORDER BY SoPhimChung DESC LIMIT 15;
```

---

## 7. Báo Cáo Học Thuật Đầy Đủ

Vui lòng tham khảo file báo cáo chi tiết:
- **[BAO_CAO_BAI_TAP_LON_SNA.pdf](./reports/BAO_CAO_BAI_TAP_LON_SNA.pdf)** (Phiên bản PDF hoàn chỉnh 11 trang kèm đồ thị phân tích).
- **[BAO_CAO_BAI_TAP_LON_SNA.md](./reports/BAO_CAO_BAI_TAP_LON_SNA.md)** (Phiên bản Markdown toàn văn $\ge 750$ dòng, 7 phần học thuật chuẩn mực).
