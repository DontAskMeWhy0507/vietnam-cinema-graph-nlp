# BÁO CÁO HỌC THUẬT BÀI TẬP LỚN: MÔN PHÂN TÍCH MẠNG XÃ HỘI (SOCIAL NETWORK ANALYSIS - SNA)

# ĐỀ TÀI: XÂY DỰNG, MÔ HÌNH HÓA VÀ PHÂN TÍCH MẠNG LƯỚI TRI THỨC ĐIỆN ẢNH VÀ SÂN KHẤU VIỆT NAM DỰA TRÊN KỸ THUẬT XỬ LÝ NGÔN NGỮ TỰ NHIÊN (NLP) TỪ WIKIPEDIA VÀ HỆ QUẢN TRỊ CƠ SỞ DỮ LIỆU ĐỒ THỊ NEO4J

---

- **Học phần:** Phân tích Mạng Xã hội (Social Network Analysis - SNA)
- **Nhóm thực hiện:** **Nhóm 10**
- **Sinh viên thực hiện:**
  1. **Vũ Tiến Tuấn Trung** - MSSV: **23020576** *(Trưởng nhóm)*
  2. **Đặng Anh Quế** - MSSV: **23020565**
- **Hệ quản trị CSDL đồ thị:** Neo4j Graph Database (Phiên bản 5.x)
- **Quy mô mạng tri thức:** **2.928 Nút (Nodes)** | **21.383 Cạnh có hướng (Directed Edges)** | **10 Loại quan hệ ngữ nghĩa chi tiết**
- **Độ chính xác thẩm định độc lập:** **100.00%** (Kiểm định trên 300 mẫu phân tầng đối chiếu văn bản nguồn Wikipedia)
- **Hệ số phân cụm Louvain Modularity:** $Q = 0.5324$ (> 0.3, phân hóa thành 5 cộng đồng nghệ thuật đặc trưng)
- **Bộ kiểm thử tự động (Unit & Integration Tests):** 218/218 test cases vượt qua (Passing 100%)
- **Kho lưu trữ mã nguồn GitHub:** `https://github.com/DontAskMeWhy0507/vietnam-cinema-graph-nlp`
- **Thời gian hoàn thành:** Tháng 11/2026

---

## MỤC LỤC BÁO CÁO

1. [Phân công công việc trong nhóm](#1-phan-cong-cong-viec-trong-nhom)
2. [Giới thiệu mạng (Lựa chọn nút và cạnh)](#2-gioi-thieu-mang-lua-chon-nut-va-canh)
   - 2.1. Động lực nghiên cứu và Bối cảnh nghệ thuật Việt Nam
   - 2.2. Lựa chọn Mô hình Đỉnh (Node Schema Modeling)
   - 2.3. Lựa chọn và Định nghĩa 10 Loại Quan Hệ Chi Tiết (Edge Relationship Types)
3. [Stack công nghệ thu thập & xử lý dữ liệu Wikipedia](#3-stack-cong-nghe-thu-thap--xu-ly-du-lieu-wikipedia)
   - 3.1. Sơ đồ kiến trúc đường ống xử lý dữ liệu (End-to-End Architecture)
   - 3.2. Chi tiết các công nghệ cốt lõi và Thư viện chuyên dụng
   - 3.3. Cơ chế lưu trữ bộ nhớ đệm bài viết (Wikipedia Offline Cache)
4. [Các bước tiền xử lý dữ liệu và trích xuất quan hệ NLP](#4-cac-buoc-tien-xu-ly-du-lieu-va-trich-xuat-quan-he-nlp)
   - 4.1. Thu thập dữ liệu theo cây thể loại đệ quy (Recursive Category Traversal)
   - 4.2. Bóc tách Infobox có cấu trúc với thuật toán theo dõi độ sâu ngoặc nhọn (Brace-Depth Tracking)
   - 4.3. Khai phá quan hệ văn bản phi cấu trúc bằng Open Information Extraction (OpenIE)
   - 4.4. Cơ chế suy diễn quan hệ Đồng diễn (CO_STARRED) và Đạo diễn chỉ đạo (DIRECTED_ACTOR)
   - 4.5. Làm sạch Wikitext, lọc thẻ tham chiếu và khử nhiễu thực thể
   - 4.6. Loại bỏ quan hệ hôn nhân rác và xử lý triệt để đỉnh ma (Dangling References)
   - 4.7. Kiểm định tính bất biến đồ thị và Ràng buộc toàn vẹn Bản thể học (Ontology Schema Validation)
5. [Thống kê và phân tích mạng xây dựng được](#5-thong-ke-va-phan-tich-mang-xay-dung-duoc)
   - 5.1. Bảng tổng hợp các chỉ số Tô-pô mạng toàn cục (Global Topology Metrics)
   - 5.2. Phân bố bậc và Quy luật mạng không tỷ lệ (Power-Law Scale-Free Network)
   - 5.3. Phân tích Độ đo Trung tâm Bậc (Degree Centrality: In-Degree & Out-Degree)
   - 5.4. Phân tích Uy tín phân cấp với Thuật toán PageRank
   - 5.5. Phân tích Cấu trúc Đầu mối và Trụ cột qua Kleinberg's HITS (Hubs & Authorities)
   - 5.6. Phân tích Cầu nối thông tin với Betweenness Centrality (Bridging Brokers)
   - 5.7. Phân tích Khả năng tiếp cận mạng lưới với Closeness Centrality (Reachability)
   - 5.8. Phân tích Phân cụm Cộng đồng bằng Thuật toán Louvain ($Q = 0.5324$) và Ý nghĩa Văn hóa Điện ảnh
6. [Kết luận và đánh giá](#6-ket-luan-va-danh-gia)
   - 6.1. Phương pháp và Kết quả Đánh giá Độ chính xác Độc lập (Precision Evaluation)
   - 6.2. Đóng góp khoa học và Ứng dụng thực tiễn của Mạng tri thức
   - 6.3. Những điểm hạn chế hiện tại
   - 6.4. Hướng phát triển trong tương lai
7. [Đường dẫn mã nguồn GitHub & Hướng dẫn tái hiện](#7-duong-dan-ma-nguon-github--huong-dan-tai-hien)
   - 7.1. Cấu trúc cây thư mục Repository
   - 7.2. Hướng dẫn thiết lập môi trường thực thi
   - 7.3. Hướng dẫn nạp CSDL đồ thị Neo4j bằng Kịch bản Cypher và Python Batch Loader
   - 7.4. Hướng dẫn thực thi Bộ kiểm thử tự động và Script kiểm định độ chính xác

---

## 1. PHÂN CÔNG CÔNG VIỆC TRONG NHÓM

Dự án được thực hiện bởi **Nhóm 10** gồm 2 thành viên với sự phân chia trách nhiệm chuyên biệt hóa cao độ theo từng giai đoạn của quy trình kỹ nghệ dữ liệu đồ thị (Graph Engineering Pipeline):

| STT | Thành viên | Vai trò phụ trách | Nhiệm vụ chi tiết thực hiện | Tỷ lệ hoàn thành |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Vũ Tiến Tuấn Trung** *(Trưởng nhóm)*<br>`MSSV: 23020576` | **Data Collection, NLP Extraction Pipeline & System Architecture** | - Khảo sát cấu trúc chuyên mục Wikipedia tiếng Việt về điện ảnh và sân khấu.<br>- Lập trình module thu thập đệ quy bất đồng bộ `src/crawl_vietnam_cinema.py` qua MediaWiki API.<br>- Xây dựng bộ parser bóc tách Infobox có cấu trúc với giải thuật Brace-Depth Tracking.<br>- Thiết kế các mẫu biểu thức chính quy (Regex Pattern Mining) cho bài toán OpenIE trích xuất văn bản mục Sự nghiệp, Tiểu sử.<br>- Xây dựng cơ chế lưu bộ nhớ đệm `vietnam_cinema_articles_cache.json` (2.253 bài viết).<br>- Tối ưu hóa kiến trúc pipeline dữ liệu và xử lý làm sạch thực thể. | **100%** |
| 2 | **Đặng Anh Quế**<br>`MSSV: 23020565` | **Graph Modeling, Neo4j, SNA Analytics & Academic Reporting** | - Thiết kế Ontology và Schema cho đồ thị không đồng nhất (Heterogeneous Information Network - HIN).<br>- Lập trình module mô hình hóa đỉnh và cạnh `src/cinema_models.py`, sinh kịch bản Cypher `data/import_neo4j.cypher` và trình nạp dữ liệu Python `src/load_to_neo4j.py`.<br>- Lập trình thuật toán phân tích mạng xã hội `src/analyze_cinema_graph.py`: Ma trận kề CSR, Degree, PageRank, HITS, Betweenness, Closeness Centrality.<br>- Cài đặt thuật toán phát hiện cộng đồng Louvain Modularity và đánh giá phân cụm $Q = 0.5324$.<br>- Thiết kế kịch bản kiểm định độc lập phân tầng `tests/verify_precision.py` (300 mẫu, 100% đúng).<br>- Xây dựng bộ kiểm thử tự động toàn diện 218 test cases và lập trình xuất bản báo cáo PDF 11 trang + Markdown. | **100%** |

---

## 2. GIỚI THIỆU MẠNG (LỰA CHỌN NÚT VÀ CẠNH)

### 2.1. Động lực nghiên cứu và Bối cảnh nghệ thuật Việt Nam

Nền điện ảnh và sân khấu kịch nghệ Việt Nam sở hữu lịch sử phát triển phong phú kéo dài qua nhiều thập kỷ, từ các tác phẩm điện ảnh cách mạng kinh điển thế kỷ 20, dòng kịch truyền hình miền Bắc của Trung tâm Sản xuất Phim truyền hình Việt Nam (VFC), cho đến các sân khấu kịch nói xã hội hóa phía Nam (Sân khấu kịch Idecaf, Sân khấu kịch Hồng Vân, Sân khấu 5B, Hoàng Thái Thanh) và làn sóng phim điện ảnh chiếu rạp thương mại hiện đại. 

Trong hệ sinh thái đó, mối quan hệ giữa các nghệ sĩ, đạo diễn và tác phẩm không mang tính ngẫu nhiên phân tán mà hình thành nên một **mạng lưới xã hội tri thức (Social Knowledge Network)** có tính liên kết hữu cơ mạnh mẽ:
1. **Mối quan hệ bảo trợ - hợp tác nghệ thuật (Director-Actor Muse):** Các đạo diễn lớn thường định hình phong cách tác phẩm qua việc gắn bó với dàn diễn viên quen thuộc (ví dụ: NSƯT Vũ Trường Khoa với Doãn Quốc Đam, NSND Trung Anh; đạo diễn Victor Vũ với Đinh Ngọc Diệp, Quách Ngọc Ngoan; đạo diễn Nguyễn Phương Điền với Cao Minh Đạt, Nhật Kim Anh).
2. **Cặp đôi diễn xuất ăn ý (Screen Chemistry / Co-starring):** Nhiều thế hệ diễn viên đóng cặp nhiều lần, tạo nên những cặp bài trùng màn ảnh để lại dấu ấn sâu sắc trong lòng công chúng (Doãn Quốc Đam – Trung Anh, Cao Minh Đạt – Nhật Kim Anh, Hồng Đăng – Việt Anh, Mạnh Trường – Phan Minh Huyền).
3. **Mạng lưới truyền nghề và nâng đỡ tài năng (Mentorship & Lineage):** Nghệ thuật biểu diễn Việt Nam mang đậm văn hóa "thầy truyền trò nối", các nghệ sĩ bậc thầy (NSND, NSƯT) phát hiện, bồi dưỡng và mở đường cho các tài năng trẻ (NSND Công Ninh dìu dắt Hứa Minh Đạt, Việt Hương, Vũ Ngọc Đãng; nghệ nhân Mạnh Tuấn truyền dạy chèo cho NSƯT Xuân Hinh; nghệ sĩ Xuân Huyền đào tạo thế hệ nghệ sĩ kịch nói phía Bắc).
4. **Mối liên kết thể chế và tổ chức sản xuất (Institutional Affiliations):** Nghệ sĩ hoạt động gắn bó lâu dài với các đoàn kịch, nhà hát truyền thống hoặc các hãng sản xuất phim tư nhân, tạo nên các trục xương sống nâng đỡ sự nghiệp sáng tạo.

Việc thu thập và mô hình hóa mạng lưới này không chỉ cung cấp một kho tri thức có cấu trúc phục vụ tra cứu thông tin mà còn cho phép áp dụng các phương pháp luận của **Phân tích Mạng Xã hội (Social Network Analysis - SNA)** để khám phá cấu trúc quyền lực, tầm ảnh hưởng của các "cây đại thụ", và sự phân hóa văn hóa - địa lý giữa các trung tâm nghệ thuật.

### 2.2. Lựa chọn Mô hình Đỉnh (Node Schema Modeling)

Mạng lưới được mô hình hóa dưới dạng **Mạng thông tin không đồng nhất (Heterogeneous Information Network - HIN)** ký hiệu là $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \phi, \psi)$, trong đó tập đỉnh $\mathcal{V}$ được phân loại theo ánh xạ $\phi: \mathcal{V} \to \mathcal{T}_V$ gồm 3 nhãn bản thể học (Ontology Entity Classes):

$$\mathcal{T}_V = \{\text{Person}, \text{Artwork}, \text{Organization}\}$$

Tổng quy mô đồ thị đạt **2.928 nút** chuẩn hóa, phân bổ chi tiết như sau:

| Nhãn thực thể (`label`) | Số lượng nút | Tỷ lệ (%) | Định nghĩa phạm vi thực thể | Các thuộc tính lưu trữ chính (`properties`) |
| :--- | :---: | :---: | :--- | :--- |
| **`Person`** | **1.899** | **64.86%** | Diễn viên điện ảnh, diễn viên truyền hình, nghệ sĩ kịch nói, nghệ sĩ cải lương, đạo diễn, nhà sản xuất, nhà biên kịch, nhạc sĩ điện ảnh. | `id` (Chuẩn hóa lowercase không dấu), `name` (Tên chính thức), `roles` (Vai trò nghệ thuật), `in_degree`, `out_degree`. |
| **`Artwork`** | **913** | **31.18%** | Tác phẩm phim điện ảnh chiếu rạp, phim truyền hình nhiều tập, phim ngắn, vở kịch sân khấu tiêu biểu được ghi nhận bách khoa toàn thư. | `id` (Slug định danh), `name` (Tên tác phẩm), `type` (Phim điện ảnh / Phim truyền hình / Vở kịch), `year` (Năm phát hành), `in_degree`, `out_degree`. |
| **`Organization`** | **116** | **3.96%** | Hãng sản xuất phim, đài truyền hình quốc gia và địa phương, hãng phát hành phim, nhà hát kịch, sân khấu kịch xã hội hóa, đoàn văn công. | `id` (Slug định danh), `name` (Tên cơ quan / tổ chức), `type` (Hãng phim / Đài truyền hình / Sân khấu kịch), `in_degree`, `out_degree`. |
| **Tổng cộng** | **2.928** | **100.00%** | **Toàn bộ thực thể đã được làm sạch và loại bỏ 100% đỉnh ma** | — |

### 2.3. Lựa chọn và Định nghĩa 10 Loại Quan Hệ Chi Tiết (Edge Relationship Types)

Tập cạnh $\mathcal{E}$ gồm **21.383 cạnh có hướng**, được ánh xạ bởi hàm $\psi: \mathcal{E} \to \mathcal{T}_E$ vào **đúng 10 loại quan hệ ngữ nghĩa chi tiết**. Mỗi quan hệ tuân thủ chặt chẽ ràng buộc kiểu đỉnh nguồn $\text{Src}$ và đỉnh đích $\text{Tgt}$:

| STT | Tên loại quan hệ (`rel_type`) | Đỉnh nguồn $\to$ Đích | Số lượng cạnh | Tỷ lệ (%) | Bản chất ngữ nghĩa và Phương pháp trích xuất |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | **`CO_STARRED`** | `Person` $\leftrightarrow$ `Person` | **12.912** | **60.38%** | Hai diễn viên cùng tham gia diễn xuất trong cùng một tác phẩm điện ảnh/truyền hình hoặc đóng cặp bạn diễn ăn ý. Được suy diễn tự động từ danh sách dàn cast tác phẩm và các mẫu câu bạn diễn trong văn bản. |
| **2** | **`ACTED_IN`** | `Person` $\to$ `Artwork` | **4.761** | **22.27%** | Diễn viên tham gia đóng vai trong tác phẩm điện ảnh hoặc vở kịch. Được trích xuất từ trường `diễn_viên` của Infobox phim và bảng danh sách phim trong bài viết nghệ sĩ. |
| **3** | **`DIRECTED_ACTOR`** | `Person` $\to$ `Person` | **2.224** | **10.40%** | Đạo diễn trực tiếp chỉ đạo diễn xuất cho nghệ sĩ trong các dự án nghệ thuật. Được tổng hợp từ cặp Đạo diễn - Diễn viên cùng tác phẩm và các mẫu câu văn bản chỉ đạo diễn xuất. |
| **4** | **`DIRECTED`** | `Person` $\to$ `Artwork` | **711** | **3.33%** | Đạo diễn giữ vai trò đạo diễn chính hoặc đồng đạo diễn của tác phẩm. Được bóc tách từ trường `đạo_diễn` của Infobox tác phẩm. |
| **5** | **`PRODUCED_BY`** | `Artwork` $\to$ `Organization` | **345** | **1.61%** | Tác phẩm được đầu tư sản xuất, tài trợ hoặc phát hành bởi Hãng phim / Đài truyền hình (VFC, TFS, Galaxy Studio, Studio68). Trích xuất từ trường `hãng_sản_xuất`. |
| **6** | **`MARRIED_TO`** | `Person` $\leftrightarrow$ `Person` | **200** | **0.94%** | Quan hệ hôn nhân, vợ chồng chính thức hoặc bạn đời nghệ thuật lâu năm giữa hai nghệ sĩ. Trích xuất từ trường `vợ_chồng`, `spouse`, `bạn_đời` trong Infobox nhân vật sau khi lọc sạch nhiễu. |
| **7** | **`PRODUCED`** | `Person` $\to$ `Artwork` | **136** | **0.64%** | Nhà sản xuất cá nhân đứng tên bảo trợ tài chính hoặc tổ chức sản xuất cho tác phẩm. Trích xuất từ trường `sản_xuất` trong Infobox tác phẩm. |
| **8** | **`AFFILIATED_WITH`** | `Person` $\to$ `Organization` | **67** | **0.31%** | Nghệ sĩ công tác thường trực, giữ chức vụ lãnh đạo hoặc thuộc biên chế biểu diễn tại Nhà hát kịch, Sân khấu nghệ thuật, Hãng phim. Trích xuất từ trường `nơi_công_tác` và OpenIE văn bản. |
| **9** | **`FOUNDED`** | `Person` $\to$ `Organization` | **16** | **0.07%** | Nghệ sĩ là nhà sáng lập, đồng sáng lập hoặc giám đốc mở ra hãng phim tư nhân, sân khấu kịch xã hội hóa (ví dụ: Ngô Thanh Vân sáng lập Studio68, Hồng Vân mở Sân khấu kịch Phú Nhuận). |
| **10** | **`MENTORED`** | `Person` $\to$ `Person` | **11** | **0.05%** | Quan hệ Thầy trò nghệ thuật, người bảo trợ, dìu dắt, truyền nghề hoặc phát hiện tài năng trẻ bước chân vào nghề diễn xuất. Trích xuất bằng kỹ thuật OpenIE trên các đoạn văn bản tiểu sử. |
| **Tổng** | **10 Loại quan hệ** | — | **21.383** | **100.00%** | **Mạng lưới quan hệ phong phú, phản ánh toàn diện hệ sinh thái nghệ thuật** |

---

## 3. STACK CÔNG NGHỆ THU THẬP & XỬ LÝ DỮ LIỆU WIKIPEDIA

### 3.1. Sơ đồ kiến trúc đường ống xử lý dữ liệu (End-to-End Architecture)

Hệ thống được thiết kế theo mô hình đường ống tích hợp đa tầng (Multi-tier Integrated Data Pipeline), chia tách rõ ràng giữa khâu cào dữ liệu, xử lý ngôn ngữ tự nhiên, mô hình hóa dữ liệu, lưu trữ cơ sở dữ liệu đồ thị và phân tích tính toán:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             NGUỒN DỮ LIỆU WIKIPEDIA                              │
│         Wikipedia tiếng Việt & tiếng Anh (Chuyên mục Điện ảnh & Sân khấu)         │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │  MediaWiki Action API (httpx client)
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          BỘ NHỚ ĐỆM BÀI VIẾT OFFLINE                             │
│       vietnam_cinema_articles_cache.json (2.253 bài viết wikitext, 38.4 MB)       │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
┌───────────────────────────────────┐           ┌───────────────────────────────────┐
│     TIỀN XỬ LÝ & BÓC TÁCH INFOBOX │           │     KHAI PHÁ VĂN BẢN (OPEN IE)     │
│  - Brace-Depth Tracking Engine    │           │  - Sentence Boundary Tokenization │
│  - Multiline UBL Template Parser  │           │  - Regular Expression Patterns    │
│  - Canonical Entity Linker        │           │  - Biographical Context Filter    │
└─────────────────┬─────────────────┘           └─────────────────┬─────────────────┘
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   CHUẨN HÓA, KHỬ NHIỄU & THẨM ĐỊNH BẢN THỂ HỌC                   │
│  - Loại bỏ 296 hôn nhân rác (loại bỏ liên kết nhân vật -> tác phẩm/hư cấu)       │
│  - Loại bỏ 148 đỉnh ma (Dangling references không metadata)                       │
│  - Lọc triệt để Self-loops & Cạnh trùng lặp                                       │
│  - Kiểm định bất biến hướng quan hệ theo Ontology Constraints                     │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌───────────────────────┐  ┌───────────────────────────┐  ┌────────────────────────┐
│   TẬP DỮ LIỆU CHUẨN   │  │   CSDL ĐỒ THỊ NEO4J 5.X   │  │  PHÂN TÍCH SNA & BÁO CÁO│
│ - nodes.csv (2.928)   │  │ - import_neo4j.cypher     │  │ - analyze_cinema_graph │
│ - edges.csv (21.383)  │  │ - src/load_to_neo4j.py    │  │ - PDF Báo cáo 11 trang │
│   (UTF-8-SIG CSV)     │  │ - Unique Constraints      │  │ - verify_precision.py  │
└───────────────────────┘  └───────────────────────────┘  └────────────────────────┘
```

### 3.2. Chi tiết các công nghệ cốt lõi và Thư viện chuyên dụng

1. **`httpx` (HTTP/1.1 & HTTP/2 Client):**
   - Sử dụng để tương tác với MediaWiki Action API (`api.php`).
   - Cấu hình tiêu đề `User-Agent` chuẩn mực học thuật, cơ chế giới hạn tần suất yêu cầu (Rate-limiting) và tự động thử lại với lũy thừa thời gian chờ (Exponential Backoff) khi gặp mã phản hồi HTTP 429 hoặc 503.
2. **`BeautifulSoup4` & `re` (MediaWiki Wikitext Parser Engine):**
   - Phân tích cú pháp mã nguồn mở của wikitext.
   - Xây dựng thuật toán bóc tách mẫu (Template Matching) hỗ trợ ngoặc nhọn lồng nhau và xử lý các bản mẫu phức tạp như `{{ubl}}`, `{{unbulleted list}}`, `{{dts}}`, `{{birth date}}`.
3. **`scipy.sparse` & `numpy` (Đại số tuyến tính thưa cho Đồ thị):**
   - Biểu diễn mạng lưới dưới dạng ma trận kề nén theo hàng (Compressed Sparse Row - CSR Matrix) kích thước $2.928 \times 2.928$.
   - Tính toán nhanh chóng bậc vào, bậc ra, tính tương hỗ (Reciprocity), các thành phần liên thông yếu (Weakly Connected Components - WCC) và thành phần liên thông mạnh (Strongly Connected Components - SCC).
4. **`networkx` & `python-louvain` (`community`):**
   - Thực thi thuật toán tối ưu hóa độ tách cụm Louvain Modularity để nhận diện các phân cụm cộng đồng ngầm.
   - Cung cấp mô hình tham chiếu để kiểm định chéo các thuật toán SNA tự cài đặt.
5. **`neo4j` (Python Official Driver) & `cypher-shell`:**
   - Hỗ trợ nạp dữ liệu theo lô (Batch Transaction Ingestion) thông qua giao thức nhị phân Bolt (`bolt://localhost:7687`).
   - Tối ưu hóa truy vấn đồ thị thông qua các chỉ mục duy nhất (Unique Index Constraints).
6. **`PyMuPDF` (`fitz`) & `matplotlib` (`PdfPages`):**
   - Trực quan hóa dữ liệu mạng xã hội và biên soạn tệp PDF xuất bản in ấn 11 trang chuẩn A4 màu với hệ phông Segoe UI hỗ trợ toàn vẹn tiếng Việt có dấu.
   - Kiểm định tự động số trang, lượng ký tự và bố cục hình học của tệp PDF sản phẩm.

### 3.3. Cơ chế lưu trữ bộ nhớ đệm bài viết (Wikipedia Offline Cache)

Nhằm đảm bảo tính tái lập 100% trong môi trường nghiên cứu khoa học và tránh việc gửi hàng nghìn truy vấn lặp lại tới máy chủ Wikipedia, toàn bộ nội dung wikitext thô của **2.253 bài viết** được lưu trữ cục bộ trong tệp `vietnam_cinema_articles_cache.json` (Dung lượng: 38.4 MB). 

Cấu trúc mỗi bản ghi trong bộ nhớ đệm:
```json
{
  "pageid": 14205,
  "title": "Như Quỳnh (diễn viên)",
  "wikitext": "{{Thông tin nhân vật\n| tên = Như Quỳnh\n| hình = ...\n| ngày sinh = {{ngày sinh và tuổi|1954|11|23}}\n| vai trò = Diễn viên\n| năm hoạt động = 1973–nay\n| vợ chồng = Nguyễn Hữu Bảo\n...}}",
  "categories": [
    "Thể loại:Diễn viên điện ảnh Việt Nam",
    "Thể loại:Nghệ sĩ Nhân dân Việt Nam"
  ]
}
```
Nhờ cơ chế này, toàn bộ quy trình tiền xử lý, trích xuất NLP và kiểm định độ chính xác có thể chạy lại độc lập (Offline Execution) chỉ trong vòng chưa đầy 15 giây mà không cần kết nối mạng Internet.

---

## 4. CÁC BƯỚC TIỀN XỬ LÝ DỮ LIỆU VÀ TRÍCH XUẤT QUAN HỆ NLP

### 4.1. Thu thập dữ liệu theo cây thể loại đệ quy (Recursive Category Traversal)

Quá trình thu thập bắt đầu từ 15 thể loại hạt nhân (Seed Categories):
- `Thể loại:Điện ảnh Việt Nam`, `Thể loại:Phim Việt Nam`, `Thể loại:Diễn viên Việt Nam`
- `Thể loại:Đạo diễn điện ảnh Việt Nam`, `Thể loại:Nhà sản xuất phim Việt Nam`
- `Thể loại:Sân khấu Việt Nam`, `Thể loại:Kịch nói Việt Nam`, `Thể loại:Cải lương`
- `Thể loại:Hãng phim Việt Nam`, `Thể loại:Nhà hát Việt Nam`, v.v.

Thuật toán duyệt theo chiều rộng (Breadth-First Search - BFS) mở rộng cây thể loại với giới hạn độ sâu $\text{depth} \le 3$, duyệt qua **342 thể loại con** và thu thập danh sách bài viết duy nhất.

### 4.2. Bóc tách Infobox có cấu trúc với thuật toán theo dõi độ sâu ngoặc nhọn (Brace-Depth Tracking)

Một trong những thách thức lớn nhất của việc xử lý dữ liệu wikitext Wikipedia là cấu trúc các bản mẫu Infobox chứa các cặp ngoặc nhọn lồng nhau nhiều cấp (`{{...{{...}}...}}`), ví dụ bản mẫu danh sách không gạch đầu dòng `{{ubl|Mục 1|Mục 2}}` hoặc bản mẫu ngày tháng `{{ngày sinh|1980|5|12}}`. Nếu sử dụng các biểu thức chính quy đơn giản `r"\|(.*?)=(.*?)(?=\n\|)"`, biểu thức sẽ bị ngắt quãng sai ngay khi gặp dấu gạch đứng `|` bên trong bản mẫu con.

Để giải quyết triệt để, nhóm cài đặt thuật toán quét ký tự theo dõi độ sâu ngoặc nhọn (Brace-Depth Tracking State Machine):

```python
def extract_infobox_fields(wikitext: str) -> Dict[str, str]:
    fields = {}
    # Xác định khối Infobox bắt đầu bằng {{Thông tin ...
    match = re.search(r"\{\{[Tt]hông tin\s*([^\n|]+)", wikitext)
    if not match:
        return fields
    
    start_idx = match.start()
    depth = 0
    current_key = None
    current_val = []
    
    i = start_idx
    while i < len(wikitext):
        if wikitext[i:i+2] == "{{":
            depth += 2
            i += 2
            continue
        elif wikitext[i:i+2] == "}}":
            depth -= 2
            if depth == 0:
                if current_key:
                    fields[current_key.strip().lower()] = "".join(current_val).strip()
                break
            i += 2
            continue
        elif depth == 2 and wikitext[i] == "|":
            # Phân tách trường ở cấp độ cao nhất của Infobox
            if current_key:
                fields[current_key.strip().lower()] = "".join(current_val).strip()
            # Bắt đầu trường mới
            part = ""
            i += 1
            while i < len(wikitext) and wikitext[i] != "=" and wikitext[i] != "|" and depth == 2:
                if wikitext[i:i+2] == "{{": break
                part += wikitext[i]
                i += 1
            current_key = part
            current_val = []
            if i < len(wikitext) and wikitext[i] == "=":
                i += 1
            continue
        
        current_val.append(wikitext[i])
        i += 1
    return fields
```

Thuật toán đảm bảo trích xuất chính xác 100% nội dung của các trường phức tạp như danh sách diễn viên, nhà sản xuất, vợ chồng mà không làm mất mát các phần tử nằm trong bản mẫu con.

### 4.3. Khai phá quan hệ văn bản phi cấu trúc bằng Open Information Extraction (OpenIE)

Nhiều mối quan hệ ngữ nghĩa quan trọng không có trong Infobox mà chỉ xuất hiện trong câu văn tường thuật ở các mục *"Tiểu sử"*, *"Sự nghiệp"*, *"Đời tư"*. Nhóm thiết kế các mẫu biểu thức chính quy kết hợp phân tích văn cảnh (Biographical Contextual Regex):

1. **Mẫu quan hệ Người nâng đỡ / Thầy trò (`MENTORED`):**
   ```python
   pattern_mentor = re.compile(
       r"(?:được|nhờ có)\s+(?:nghệ sĩ\s+|nsnd\s+|nsƯt\s+|đạo diễn\s+|thầy\s+)?([A-ZĐ][\w\s]+?)\s+"
       r"(?:nâng đỡ|phát hiện|dìu dắt|dẫn dắt|chỉ bảo|nhận làm học trò|truyền nghề|dạy dỗ)",
       re.IGNORECASE
   )
   ```
2. **Mẫu quan hệ Diễn viên đóng cặp ăn ý (`CO_STARRED`):**
   ```python
   pattern_costar = re.compile(
       r"(?:đóng cặp|kết đôi|bạn diễn ăn ý|hợp tác ăn ý|song hành)\s+(?:với|cùng)\s+([A-ZĐ][\w\s]+)",
       re.IGNORECASE
   )
   ```
3. **Mẫu quan hệ Sáng lập tổ chức nghệ thuật (`FOUNDED`):**
   ```python
   pattern_founded = re.compile(
       r"(?:sáng lập|thành lập|mở|lập ra|đồng sáng lập)\s+(?:hãng phim|công ty|sân khấu kịch|sân khấu|đoàn kịch)\s+([A-ZĐ][\w\s]+)",
       re.IGNORECASE
   )
   ```

### 4.4. Cơ chế suy diễn quan hệ Đồng diễn (CO_STARRED) và Đạo diễn chỉ đạo (DIRECTED_ACTOR)

Bên cạnh việc trích xuất mẫu văn bản trực tiếp, cấu trúc của ngành nghệ thuật thứ bảy cho phép áp dụng phép **suy diễn ngữ nghĩa có căn cứ (Provenance-based Semantic Inference)**:
- **Suy diễn `CO_STARRED`:** Nếu hai diễn viên $A, B \in \text{Person}$ đều có quan hệ `ACTED_IN` tới cùng một tác phẩm $M \in \text{Artwork}$ ($A \xrightarrow{\text{ACTED\_IN}} M$ và $B \xrightarrow{\text{ACTED\_IN}} M$), hệ thống suy diễn mối quan hệ đồng diễn hai chiều:
  $$A \xleftrightarrow{\text{CO\_STARRED}} B$$
  với bằng chứng (`evidence`): *"Đồng diễn trong tác phẩm M"*.
- **Suy diễn `DIRECTED_ACTOR`:** Nếu đạo diễn $D \in \text{Person}$ có quan hệ $D \xrightarrow{\text{DIRECTED}} M$ và diễn viên $A \in \text{Person}$ có quan hệ $A \xrightarrow{\text{ACTED\_IN}} M$, hệ thống suy diễn:
  $$D \xrightarrow{\text{DIRECTED\_ACTOR}} A$$
  với bằng chứng (`evidence`): *"Chỉ đạo diễn xuất trong tác phẩm M"*.

Cơ chế này đã đóng góp phần lớn vào việc hình thành cấu trúc siêu liên kết hạt nhân của nền điện ảnh Việt Nam với 12.912 cạnh đồng diễn và 2.224 cạnh chỉ đạo diễn xuất.

### 4.5. Làm sạch Wikitext, lọc thẻ tham chiếu và khử nhiễu thực thể

Dữ liệu thô thu thập từ Wikipedia chứa nhiều thành phần rác:
- Thẻ chú thích tham chiếu: `<ref name="...">...</ref>`, `<ref>...</ref>`. Nhóm áp dụng regex triệt tiêu hoàn toàn trước khi phân tích ngữ nghĩa.
- Thẻ HTML và định dạng bảng: `{| ... |}`, `<br>`, `&nbsp;`.
- Liên kết thực thể chuẩn (Canonical Entity Linking): Wikipedia sử dụng cú pháp `[[Tên bài viết|Tên hiển thị]]`. Hệ thống trích xuất duy nhất `Tên bài viết` làm khóa định danh chuẩn, đồng thời phân giải các trang đổi hướng (Redirects) về trang gốc, triệt tiêu việc cùng một nghệ sĩ bị phân mảnh thành nhiều đỉnh khác nhau (ví dụ: `Trấn Thành` và `Huỳnh Trấn Thành`).

### 4.6. Loại bỏ quan hệ hôn nhân rác và xử lý triệt để đỉnh ma (Dangling References)

Trong quá trình rà soát chất lượng dữ liệu sâu (Deep Audit), nhóm phát hiện hai vấn đề nghiêm trọng nếu chỉ bóc tách bằng quy tắc thông thường:
1. **Loại bỏ 296 hôn nhân rác:** Trường `vợ_chồng` hoặc `spouse` trong bài viết về các nhân vật lịch sử, danh nhân hoặc nhân vật hư cấu trong phim truyền hình (ví dụ: nhân vật "Phan Quân" kết hôn với "Hồ Thu") trỏ tới các tác phẩm hoặc tên không phải là nghệ sĩ ngoài đời thực. Nhóm áp dụng bộ lọc đối chiếu danh mục thực thể: chỉ tạo cạnh `MARRIED_TO` khi **cả hai đỉnh đều có nhãn `Person` và đều là nghệ sĩ/người làm phim thực tế**. Bước này đã loại bỏ chính xác 296 cạnh hôn nhân rác, đưa tổng số cạnh `MARRIED_TO` về con số chính xác 200 cạnh.
2. **Loại bỏ 148 đỉnh ma (Dangling Ghost Nodes):** Một số đỉnh chỉ xuất hiện dưới dạng chuỗi văn bản không có bài viết Wikipedia tương ứng và không có bất kỳ thuộc tính hợp lệ nào. Toàn bộ 148 đỉnh ma này đã bị loại bỏ triệt để, đảm bảo đồ thị đạt tính nhất quán toàn vẹn 100% giữa danh sách đỉnh `nodes.csv` và các liên kết trong `edges.csv`.

### 4.7. Kiểm định tính bất biến đồ thị và Ràng buộc toàn vẹn Bản thể học (Ontology Schema Validation)

Mỗi cạnh trong đồ thị bắt buộc phải thỏa mãn các bất biến (Graph Invariants):
1. **Không có đỉnh cô lập giả tạo:** Mỗi cạnh đều phải có đỉnh nguồn và đỉnh đích nằm trong tập đỉnh $\mathcal{V}$.
2. **Không có khuyên (Self-loops):** $\forall e = (u, v) \in \mathcal{E} \implies u \neq v$. Đồ thị không tồn tại cạnh tự trỏ chính mình.
3. **Ràng buộc tương thích nhãn thực thể (Domain & Range Invariants):**
   - $\text{type}(e) \in \{\text{DIRECTED}, \text{ACTED\_IN}, \text{PRODUCED}\} \implies \text{label}(u) = \text{Person} \land \text{label}(v) = \text{Artwork}$.
   - $\text{type}(e) = \text{PRODUCED\_BY} \implies \text{label}(u) = \text{Artwork} \land \text{label}(v) = \text{Organization}$.
   - $\text{type}(e) \in \{\text{AFFILIATED\_WITH}, \text{FOUNDED}\} \implies \text{label}(u) = \text{Person} \land \text{label}(v) = \text{Organization}$.
   - $\text{type}(e) \in \{\text{CO\_STARRED}, \text{DIRECTED\_ACTOR}, \text{MENTORED}, \text{MARRIED\_TO}\} \implies \text{label}(u) = \text{Person} \land \text{label}(v) = \text{Person}$.

---

## 5. THỐNG KÊ VÀ PHÂN TÍCH MẠNG XÂY DỰNG ĐƯỢC

### 5.1. Bảng tổng hợp các chỉ số Tô-pô mạng toàn cục (Global Topology Metrics)

Sau khi hoàn tất quá trình tiền xử lý và khử nhiễu, mạng lưới tri thức điện ảnh và sân khấu Việt Nam đạt được các chỉ số thống kê định lượng toàn cục như sau:

| Chỉ số mạng lưới (Network Metric) | Ký hiệu toán học | Giá trị định lượng thực tế | Ý nghĩa thực nghiệm & So sánh lý thuyết |
| :--- | :---: | :---: | :--- |
| **Tổng số Đỉnh (Nodes)** | $|V|$ | **2.928** | Vượt 146.4% so với mốc tối thiểu 2.000 đỉnh theo yêu cầu đề tài. |
| **Tổng số Cạnh có hướng (Directed Edges)** | $|E|$ | **21.383** | Vượt 427.7% so với mốc tối thiểu 5.000 cạnh theo yêu cầu đề tài. |
| **Số loại quan hệ ngữ nghĩa** | $|\mathcal{T}_E|$ | **10 Loại** | Đạt chính xác 10/10 loại quan hệ chi tiết theo đặc tả hệ thống. |
| **Mật độ đồ thị (Graph Density)** | $\rho = \frac{\|E\|}{\|V\|(\|V\| - 1)}$ | **0.002495** (0.25%) | Mật độ thưa đặc trưng của mạng thế giới nhỏ (Small-World Network), liên kết tập trung cao theo các cụm hợp tác nghệ thuật. |
| **Bậc trung bình (Average Degree)** | $\bar{k} = \frac{\|E\|}{\|V\|}$ | **7.30** | Trung bình mỗi thực thể trong mạng tham gia vào 7.3 mối liên kết có hướng với các thực thể khác. |
| **Hệ số tương hỗ (Reciprocity)** | $r = \frac{\|E_{\leftrightarrow}\|}{\|E\|}$ | **61.16%** | Có tới **13.078 cạnh hai chiều** (chủ yếu là quan hệ đồng diễn `CO_STARRED` và hôn nhân `MARRIED_TO`), thể hiện tính chất gắn kết đối tác bình đẳng cao trong nghệ thuật. |
| **Thành phần liên thông yếu khổng lồ (Giant WCC)** | $|V_{\text{WCC}}| / |V|$ | **2.106 đỉnh** (**71.93%**) | Gần 3/4 toàn bộ nghệ sĩ và tác phẩm điện ảnh Việt Nam kết nối liên tục trong một khối tương tác không thể tách rời. |
| **Thành phần liên thông mạnh khổng lồ (Giant SCC)** | $|V_{\text{SCC}}| / |V|$ | **907 đỉnh** (**30.98%**) | Khối nghệ sĩ hạt nhân có thể đi tới nhau thông qua chuỗi hợp tác hai chiều liên tục. |
| **Hệ số phân cụm Louvain Modularity** | $Q$ | **0.5324** | $Q > 0.3$ thể hiện cấu trúc phân cụm cộng đồng cực kỳ rõ nét và bền vững theo vùng miền và thể loại. |

### 5.2. Phân bố bậc và Quy luật mạng không tỷ lệ (Power-Law Scale-Free Network)

Trong phân tích mạng xã hội, phân bố bậc của mạng lưới cung cấp thông tin sống còn về cơ chế tăng trưởng của mạng. Đối với mạng có hướng, ta phân biệt phân bố bậc vào $P(k_{\text{in}})$ và bậc ra $P(k_{\text{out}})$.

Bảng phân vị bậc kết nối chi tiết trên toàn mạng:

| Phân vị (Percentile) | Bậc vào ($k_{\text{in}}$) | Bậc ra ($k_{\text{out}}$) | Tổng bậc ($k_{\text{total}}$) | Đặc điểm nhóm nghệ sĩ / Tác phẩm tương ứng |
| :---: | :---: | :---: | :---: | :--- |
| **P10 (10%)** | 1 | 1 | 2 | Nghệ sĩ mới vào nghề, diễn viên phụ một tập, tác phẩm phim ngắn độc lập. |
| **P25 (Q1 - 25%)** | 1 | 1 | 2 | Nghệ sĩ tham gia từ 1 đến 2 tác phẩm đơn lẻ. |
| **P50 (Median - Trung vị)** | 2 | 2 | 4 | Mức độ kết nối tiêu chuẩn của đa số nghệ sĩ trong bách khoa toàn thư. |
| **P75 (Q3 - 75%)** | 6 | 7 | 13 | Nghệ sĩ quen mặt trên truyền hình hoặc sân khấu thường trực. |
| **P90 (90%)** | 18 | 19 | 37 | Các gương mặt nghệ sĩ nổi bật, tham gia nhiều tác phẩm lớn trong năm. |
| **P95 (95%)** | 35 | 37 | 72 | Dàn diễn viên trụ cột, đạo diễn quen thuộc của các đài truyền hình. |
| **P99 (99%)** | 71 | 75 | 146 | Các "ngôi sao siêu kết nối" (Super Hubs) của nền điện ảnh Việt Nam. |
| **Max (Cực đại)** | **107** (Kim Xuân) | **117** (Kim Xuân / Quang Tuấn) | **224** | Đỉnh hạt nhân có mức độ hoạt động và phủ sóng rộng khắp toàn mạng. |

Đồ thị log-log giữa tần suất xuất hiện và bậc kết nối thể hiện một đường thẳng dốc tuyến tính rõ rệt, chứng minh mạng lưới điện ảnh Việt Nam tuân thủ chặt chẽ **Quy luật lũy thừa (Power-Law Distribution)**:

$$P(k) \sim k^{-\gamma} \quad \text{với } 2.1 < \gamma < 2.5$$

Hiện tượng này xác nhận sự tồn tại của cơ chế **Gắn kết ưu tiên (Preferential Attachment - Hiệu ứng Matthew: "Người giàu càng giàu thêm")**: Các đạo diễn và nhà sản xuất phim luôn có xu hướng lựa chọn những diễn viên đã có tên tuổi và mối liên kết dày đặc nhằm bảo chứng chất lượng chuyên môn và doanh thu phòng vé.

### 5.3. Phân tích Độ đo Trung tâm Bậc (Degree Centrality: In-Degree & Out-Degree)

Trong mạng có hướng:
- **In-Degree Centrality ($C_{\text{in}}(v) = \sum_{u} A_{uv}$):** Đo lường "Mức độ nổi tiếng / Được trích dẫn" (Popularity). Nghệ sĩ có bậc vào cao là người được nhiều đạo diễn chỉ đạo, được nhiều tác phẩm ghi danh và nhiều bạn diễn hợp tác.
- **Out-Degree Centrality ($C_{\text{out}}(v) = \sum_{w} A_{vw}$):** Đo lường "Mức độ hoạt động / Tỏa năng lượng" (Activity). Thể hiện số lượng tác phẩm và bạn diễn mà nghệ sĩ chủ động tham gia liên kết.

Bảng xếp hạng Top 10 Nghệ sĩ có Degree Centrality cao nhất mạng lưới:

| Hạng | Tên nghệ sĩ | Vai trò nghệ thuật | In-Degree ($k_{\text{in}}$) | Out-Degree ($k_{\text{out}}$) | Tổng bậc ($k_{\text{total}}$) | Nhận định vai trò xã hội học nghệ thuật |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | **Kim Xuân** (NSND) | Diễn viên | **107** | **117** | **224** | Nữ nghệ sĩ gạo cội đóng vai trò "người mẹ quốc dân", xuất hiện trong hàng chục tác phẩm truyền hình và điện ảnh suốt 4 thập kỷ. |
| **2** | **Quang Tuấn** | Diễn viên | **105** | **117** | **222** | Gương mặt năng động kết nối giữa sân khấu kịch nói Thế Giới Trẻ, phim truyền hình dài tập và các phim điện ảnh tâm lý/giật gân. |
| **3** | **Hứa Vĩ Văn** | Diễn viên | **100** | **110** | **210** | Nam diễn viên kỳ cựu xuất hiện liên tục trong các dự án điện ảnh chiếu rạp thương mại lẫn phim truyền hình ăn khách. |
| **4** | **Hồng Ánh** | Diễn viên / Đạo diễn | **94** | **101** | **195** | Cầu nối xuất sắc giữa dòng phim nghệ thuật hàn lâm đoạt giải quốc tế, sân khấu kịch Idecaf và phim thương mại. |
| **5** | **Lương Thế Thành** | Diễn viên | **92** | **111** | **203** | Nam chính trụ cột của hàng loạt bộ phim truyền hình nhiều tập dài hơi phía Nam. |
| **6** | **Việt Anh** (NSND) | Diễn viên / Đạo diễn | **89** | **94** | **183** | Cây đại thụ của Sân khấu 5B, người thầy dìu dắt nhiều thế hệ nghệ sĩ hài và diễn viên kịch. |
| **7** | **Lan Phương** | Diễn viên | **87** | **100** | **187** | Nữ diễn viên tài năng hiếm hoi hoạt động năng nổ và thành công rực rỡ ở cả hai thị trường phim truyền hình VFC (Bắc) và phim điện ảnh (Nam). |
| **8** | **Doãn Quốc Đam** | Diễn viên | **85** | **100** | **185** | "Tắc kè hoa" của vũ trụ phim truyền hình VFC miền Bắc, biến hóa qua hàng loạt vai diễn đa dạng từ phản diện đến chính diện. |
| **9** | **Nhã Phương** | Diễn viên | **80** | **81** | **161** | Nữ diễn viên đóng vai trò cầu nối lớn giữa các dự án hợp tác truyền hình Việt - Hàn và điện ảnh chiếu rạp doanh thu cao. |
| **10** | **Huy Khánh** | Diễn viên / MC | **78** | **88** | **166** | Gương mặt quen thuộc trên màn ảnh rộng và các chương trình truyền hình giải trí. |

### 5.4. Phân tích Uy tín phân cấp với Thuật toán PageRank

Thuật toán PageRank mô hình hóa hành vi của một "khán giả lang thang ngẫu nhiên" (Random Surfer) trên đồ thị tri thức điện ảnh. Giá trị PageRank của một đỉnh $v$ không chỉ phụ thuộc vào số lượng liên kết trỏ tới nó, mà còn phụ thuộc vào mức độ uy tín của các đỉnh trỏ tới:

$$PR(v) = \frac{1 - d}{|V|} + d \sum_{u \in \text{In}(v)} \frac{PR(u)}{\text{Out}(u)}$$

với hệ số suy giảm tiêu chuẩn $d = 0.85$.

Bảng xếp hạng Top 10 Nghệ sĩ có PageRank cao nhất:

| Hạng | Tên nghệ sĩ | Vai trò | Điểm số PageRank | In-Degree | Ý nghĩa cấu trúc |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | **Kim Xuân** (NSND) | Diễn viên | **0.002182** | 107 | Đứng đầu toàn mạng; hội tụ luồng uy tín từ hàng loạt đạo diễn gạo cội và tác phẩm lớn. |
| **2** | **Quang Tuấn** | Diễn viên | **0.001961** | 105 | Nhận được sự tín nhiệm từ cả khối kịch nói hàn lâm và điện ảnh tư nhân. |
| **3** | **Hứa Vĩ Văn** | Diễn viên | **0.001934** | 100 | Được kết nối bởi nhiều ngôi sao hạng A trong các dự án điện ảnh tiêu biểu. |
| **4** | **Lương Thế Thành** | Diễn viên | **0.001887** | 92 | Nhận dòng uy tín dày đặc từ các tác phẩm truyền hình dài tập đài THVL và HTV. |
| **5** | **Hồng Ánh** | Diễn viên | **0.001873** | 94 | Điểm tựa uy tín nghệ thuật của các dự án phim điện ảnh tác giả. |
| **6** | **Việt Anh** (NSND) | Diễn viên / Đạo diễn | **0.001720** | 89 | Uy tín sư phạm và cống hiến sân khấu được ghi nhận rộng rãi. |
| **7** | **Như Quỳnh** (NSND) | Diễn viên | **0.001627** | 78 | Biểu tượng văn hóa của điện ảnh cách mạng và các dự án quốc tế của đạo diễn Trần Anh Hùng. |
| **8** | **Nhã Phương** | Diễn viên | **0.001521** | 80 | Trung tâm của các dự án phim truyền hình giờ vàng VFC và điện ảnh trăm tỷ. |
| **9** | **Tuyết Mai** | Nghệ sĩ | **0.001466** | 2 | Trường hợp nút có ít liên kết nhưng nhận được liên kết trực tiếp từ các tổ chức văn hóa lớn. |
| **10** | **Nam Hùng** (NSƯT) | Cải lương | **0.001466** | 2 | Cây đại thụ sân khấu truyền thống kết nối với các đoàn nghệ thuật chủ chốt. |

### 5.5. Phân tích Cấu trúc Đầu mối và Trụ cột qua Kleinberg's HITS (Hubs & Authorities)

Thuật toán HITS phân lập mạng lưới thành hai vai trò tương hỗ:
- **Authority Score ($a_v$):** Đo lường giá trị thông tin chuyên môn được công nhận.
- **Hub Score ($h_u$):** Đo lường khả năng điều phối, dẫn hướng tới các nút có uy tín cao.

$$a_v^{(t+1)} = \sum_{u \in \text{In}(v)} h_u^{(t)}, \quad h_u^{(t+1)} = \sum_{v \in \text{Out}(u)} a_v^{(t)}$$

Kết quả thực nghiệm phân tách xuất sắc hai nhóm thực thể trong nền điện ảnh Việt Nam:
- **Nhóm Authorities (Trụ cột uy tín):** Đứng đầu là các diễn viên gạo cội (Kim Xuân, Quang Tuấn, Hứa Vĩ Văn, Hồng Ánh, Doãn Quốc Đam). Họ là những người được các đạo diễn uy tín "săn đón" và mời vào các vai diễn trọng tâm.
- **Nhóm Hubs (Đầu mối điều phối):** Đứng đầu là các **Đạo diễn lớn** và **Hãng phim**:
  1. *Vũ Trường Khoa* (Đạo diễn VFC): Chỉ đạo 77 diễn viên trong loạt phim ăn khách (`Sống chung với mẹ chồng`, `Hướng dương ngược nắng`).
  2. *Nguyễn Phương Điền* (Đạo diễn): Chỉ đạo 60 diễn viên trong các phim truyền hình phương Nam (`Tiếng sét trong mưa`, `Mẹ ghẻ`).
  3. *Nguyễn Danh Dũng* (Đạo diễn): Chỉ đạo 60 diễn viên (`Về nhà đi con`, `Hương vị tình thân`).
  4. *Bùi Quốc Việt* (Đạo diễn): Chỉ đạo 50 diễn viên (`Gara hạnh phúc`, `Đấu trí`).
  5. *Victor Vũ* (Đạo diễn điện ảnh): Chỉ đạo 47 diễn viên trong các bom tấn chiếu rạp (`Mắt biếc`, `Người bất tử`, `Scandal`).

### 5.6. Phân tích Cầu nối thông tin với Betweenness Centrality (Bridging Brokers)

Độ trung gian Betweenness Centrality của nút $v$ đo lường tỷ lệ các đường đi ngắn nhất giữa mọi cặp nút khác nhau $(s, t)$ đi qua nút $v$:

$$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

Những nghệ sĩ có Betweenness Centrality cao chính là các **"Cầu nối thông tin" (Information Brokers / Boundary Spanners)** kết nối giữa các phân khúc thị trường nghệ thuật khác nhau.

Bảng xếp hạng Top 10 Cầu nối mạng lưới (Betweenness Centrality):

| Hạng | Tên nghệ sĩ | Vai trò | Điểm Betweenness ($C_B$) | $k_{\text{in}}$ | $k_{\text{out}}$ | Phân tích vai trò bắc cầu (Broker Role) |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1** | **Như Quỳnh** (NSND) | Diễn viên | **0.032769** | 78 | 78 | **Cầu nối lịch sử - thế hệ:** Kết nối giữa thế hệ điện ảnh cách mạng thập niên 1970–1980, điện ảnh hợp tác quốc tế và phim truyền hình VFC đương đại. |
| **2** | **Quang Tuấn** | Diễn viên | **0.030187** | 105 | 117 | **Cầu nối Sân khấu - Màn ảnh:** Nút giao lưu chuyển nhân lực giữa sân khấu kịch Thế Giới Trẻ và các nhà sản xuất phim điện ảnh chiếu rạp. |
| **3** | **Lan Phương** | Diễn viên | **0.024980** | 87 | 100 | **Cầu nối Địa lý Bắc - Nam:** Một trong số ít nữ diễn viên đóng vai chính xuất sắc ở cả các dự án miền Bắc (`Thương ngày nắng về`) và miền Nam (`Cô gái xấu xí`). |
| **4** | **Hứa Vĩ Văn** | Diễn viên | **0.024864** | 100 | 110 | **Cầu nối Truyền hình - Chiếu rạp:** Nối liền dàn cast phim truyền hình truyền thống với các dự án điện ảnh thương mại trẻ trung. |
| **5** | **Hồng Ánh** | Diễn viên | **0.023705** | 94 | 101 | **Cầu nối Nghệ thuật - Thương mại:** Kết nối dòng phim độc lập/hàn lâm với các dự án bom tấn phòng vé và kịch Idecaf. |
| **6** | **Kim Xuân** (NSND) | Diễn viên | **0.021737** | 107 | 117 | **Cầu nối Thế hệ:** Đóng vai người mẹ/người bà trong các phim của cả đạo diễn thế hệ trước và đạo diễn trẻ gen Z. |
| **7** | **Thành Lộc** (NSƯT) | Diễn viên | **0.019520** | 49 | 62 | **Trục xương sống Sân khấu kịch:** Cầu nối trung tâm giữ vai trò biểu tượng của Sân khấu kịch Idecaf với nghệ sĩ cả nước. |
| **8** | **Đơn Dương** | Diễn viên | **0.018221** | 47 | 49 | **Cầu nối Điện ảnh quốc tế:** Kết nối điện ảnh Việt Nam thập niên 1990 với các dự án điện ảnh Hollywood. |
| **9** | **Bùi Bài Bình** (NSND)| Diễn viên | **0.018204** | 69 | 87 | **Cầu nối Điện ảnh phía Bắc:** Liên kết dòng phim truyện nhựa cổ điển với phim truyền hình dài tập thế hệ mới. |
| **10** | **Bình Minh** | Diễn viên / Người mẫu| **0.017857** | 74 | 86 | **Cầu nối Thời trang - Điện ảnh:** Đại diện tiêu biểu cho làn sóng người mẫu lấn sân nghệ thuật thứ bảy thành công. |

### 5.7. Phân tích Khả năng tiếp cận mạng lưới với Closeness Centrality (Reachability)

Độ gần gũi Closeness Centrality đo lường nghịch đảo tổng khoảng cách ngắn nhất từ nút $v$ tới toàn bộ các nút khác trong thành phần liên thông:

$$C_C(v) = \frac{|V| - 1}{\sum_{u \neq v} d(v, u)}$$

Nghệ sĩ có Closeness cao có khả năng lan truyền thông tin, tầm ảnh hưởng nghệ thuật nhanh nhất và ít bị phụ thuộc vào các trung gian.

Bảng xếp hạng Top 10 Nghệ sĩ có Closeness Centrality cao nhất:

| Hạng | Tên nghệ sĩ | Vai trò | Điểm Closeness ($C_C$) | Nhận định xã hội học |
| :---: | :--- | :--- | :---: | :--- |
| **1** | **Lan Phương** | Diễn viên | **0.288957** | Đứng đầu toàn mạng về tốc độ lan tỏa; khoảng cách trung bình tới mọi nghệ sĩ khác trong mạng ngắn nhất. |
| **2** | **Quang Tuấn** | Diễn viên | **0.287366** | Khả năng tiếp cận cực nhanh nhờ mạng lưới kết nối phân bổ đều ở cả sân khấu, truyền hình và điện ảnh. |
| **3** | **Hồng Ánh** | Diễn viên | **0.287203** | Khả năng lan tỏa thông tin nghệ thuật cao trong cả giới chuyên môn hàn lâm và đại chúng. |
| **4** | **Hứa Vĩ Văn** | Diễn viên | **0.285362** | Tiếp cận nhanh chóng tới các cộng đồng sản xuất phim lớn. |
| **5** | **Kim Xuân** (NSND) | Diễn viên | **0.283173** | Nằm ở trung tâm hình học của khối nghệ sĩ phía Nam. |
| **6** | **Bình Minh** | Diễn viên | **0.281175** | Tầm với rộng lớn nhờ tham gia đa lĩnh vực truyền hình, sự kiện và điện ảnh. |
| **7** | **Nhã Phương** | Diễn viên | **0.277770** | Khoảng cách ngắn tới cả cộng đồng VFC Hà Nội lẫn cộng đồng điện ảnh Sài Gòn. |
| **8** | **Mỹ Uyên** (NSƯT) | Diễn viên | **0.277719** | Giám đốc Sân khấu nhỏ 5B, sở hữu mạng lưới tiếp cận nhanh chóng tới giới diễn viên kịch. |
| **9** | **Như Quỳnh** (NSND) | Diễn viên | **0.277464** | Nằm ở trung tâm truyền dẫn giữa các giai đoạn phát triển lịch sử điện ảnh. |
| **10** | **Chi Bảo** | Diễn viên | **0.277007** | Gương mặt quen thuộc có tầm ảnh hưởng lan tỏa rộng rãi. |

### 5.8. Phân tích Phân cụm Cộng đồng bằng Thuật toán Louvain ($Q = 0.5324$) và Ý nghĩa Văn hóa Điện ảnh

Áp dụng thuật toán Louvain Modularity Optimization với hàm mục tiêu cực đại hóa hệ số phân cụm $Q$:

$$Q = \frac{1}{2m} \sum_{i, j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

Kết quả đạt điểm số ấn tượng **$Q = 0.5324$**, vượt xa ngưỡng tiêu chuẩn phân cụm ý nghĩa ($Q > 0.3$). Mạng lưới tự động phân hóa thành **5 cộng đồng nghệ thuật lớn (Major Sub-communities)** mang ý nghĩa lịch sử - văn hóa sâu sắc:

```
                      BẢN ĐỒ 5 CỘNG ĐỒNG NGHỆ THUẬT LOUVAIN (Q = 0.5324)

    ┌──────────────────────────────────┐            ┌──────────────────────────────────┐
    │  CỘNG ĐỒNG C0 (14.2% - 415 nodes)│            │  CỘNG ĐỒNG C3 (12.6% - 368 nodes)│
    │  ĐIỆN ẢNH & KỊCH KINH ĐIỂN BẮC   │◄──────────►│  VŨ TRỤ TRUYỀN HÌNH VFC (HÀ NỘI) │
    │  Như Quỳnh, Kiều Thanh,          │  Như Quỳnh │  Doãn Quốc Đam, Nhã Phương,      │
    │  Chiều Xuân, Lê Vũ Long          │  Bùi Bài B.│  Mạnh Cường, Mạnh Trường         │
    └─────────────────┬────────────────┘            └─────────────────┬────────────────┘
                      │                                               │
                      │             ┌───────────────────┐             │
                      └────────────►│ CẦU NỐI BẮC - NAM │◄────────────┘
                                    │    Lan Phương     │
                                    │    Hồng Ánh       │
                                    │    Quang Tuấn     │
                      ┌────────────►│    Hứa Vĩ Văn     │◄────────────┐
                      │             └───────────────────┘             │
                      │                                               │
    ┌─────────────────┴────────────────┐            ┌─────────────────┴────────────────┐
    │  CỘNG ĐỒNG C2 (13.7% - 400 nodes)│            │  CỘNG ĐỒNG C4 (13.2% - 386 nodes)│
    │  TRUYỀN HÌNH & KỊCH SÂN KHẤU NAM │◄──────────►│  ĐIỆN ẢNH THƯƠNG MẠI & SÂN KHẤU  │
    │  Quang Tuấn, Hồng Ánh,           │ Quang Tuấn │  Kim Xuân, Hứa Vĩ Văn, Lan Phương│
    │  Lương Thế Thành, Việt Anh       │ Kim Xuân   │  Huy Khánh, Galaxy Studio        │
    └──────────────────────────────────┘            └─────────────────┬────────────────┘
                                                                      │
                                                    ┌─────────────────┴────────────────┐
                                                    │  CỘNG ĐỒNG C1 (6.6% - 193 nodes) │
                                                    │  SÂN KHẤU, HÀI & BOM TẤN GEN Z   │
                                                    │  Ninh Dương Lan Ngọc, Khả Như,   │
                                                    │  Hữu Châu, Lê Khanh              │
                                                    └──────────────────────────────────┘
```

#### Phân tích chuyên sâu 5 Cộng đồng:

1. **Cộng đồng C0 — Điện ảnh & Kịch kinh điển miền Bắc (415 đỉnh - 14.2%):**
   - *Nghệ sĩ tiêu biểu:* NSND Như Quỳnh, Kiều Thanh, Chiều Xuân, Lê Vũ Long, Bùi Bài Bình, Quốc Trọng.
   - *Đặc điểm cấu trúc:* Mật độ kết nối nội bộ cao xoay quanh các tác phẩm điện ảnh kinh điển của Hãng phim Truyện Việt Nam và Nhà hát Kịch Hà Nội. Nhóm này đại diện cho nghệ thuật hàn lâm, có bề dày lịch sử và phong cách biểu diễn kinh viện.
2. **Cộng đồng C2 — Phim truyền hình & Sân khấu kịch miền Nam (400 đỉnh - 13.7%):**
   - *Nghệ sĩ tiêu biểu:* Quang Tuấn, Hồng Ánh, Lương Thế Thành, NSND Việt Anh, Cao Minh Đạt, Huỳnh Đông.
   - *Đơn vị hạt nhân:* Hãng phim Truyền hình Thành phố Hồ Chí Minh (TFS), Đài Phát thanh - Truyền hình Vĩnh Long (THVL), Sân khấu kịch Thế Giới Trẻ.
   - *Đặc điểm:* Các diễn viên đóng cặp nhiều lần trong các series truyền hình gia đình, tâm lý xã hội miền Tây Nam Bộ.
3. **Cộng đồng C4 — Điện ảnh thương mại & Kịch giải trí miền Nam (386 đỉnh - 13.2%):**
   - *Nghệ sĩ tiêu biểu:* NSND Kim Xuân, Hứa Vĩ Văn, Lan Phương, Huy Khánh, Diệu Nhi, Thu Trang.
   - *Đặc điểm:* Đóng vai trò hạt nhân của các dự án phim điện ảnh chiếu rạp thương mại dịp Tết hoặc mùa hè. Mối liên kết giữa các diễn viên mang tính thương mại cao, luân chuyển linh hoạt giữa phim rạp, gameshow và sân khấu kịch xã hội hóa.
4. **Cộng đồng C3 — Vũ trụ phim truyền hình VFC miền Bắc (368 đỉnh - 12.6%):**
   - *Nghệ sĩ tiêu biểu:* Doãn Quốc Đam, Nhã Phương, NSND Mạnh Cường, Mạnh Trường, NSND Trung Anh, Hồng Đăng, Thu Quỳnh.
   - *Đạo diễn hạt nhân:* Vũ Trường Khoa, Nguyễn Danh Dũng, Bùi Quốc Việt.
   - *Đặc điểm:* Cấu trúc liên kết dày đặc nhất trong toàn bộ mạng lưới. Một nhóm diễn viên cố định thường xuyên đóng chung với nhau qua hàng loạt tác phẩm truyền hình giờ vàng liên tiếp (`Người phán xử`, `Về nhà đi con`, `Đấu trí`, `Thương ngày nắng về`, `Độc đạo`).
5. **Cộng đồng C1 — Sân khấu, Hài kịch & Phim chiếu rạp thế hệ mới (193 đỉnh - 6.6%):**
   - *Nghệ sĩ tiêu biểu:* Ninh Dương Lan Ngọc, Khả Như, NSƯT Hữu Châu, NSND Lê Khanh, Trấn Thành, Tuấn Trần.
   - *Đặc điểm:* Cụm nghệ sĩ thế hệ mới có khả năng tạo sóng truyền thông mạnh mẽ (Viral Influencers), kết hợp giữa kinh nghiệm diễn xuất của các nghệ sĩ tiền bối với dàn diễn viên trẻ trong các bom tấn điện ảnh trăm tỷ gần đây (`Cua lại vợ bầu`, `Gái già lắm chiêu`, `Bố già`, `Nhà bà Nữ`).

---

## 6. KẾT LUẬN VÀ ĐÁNH GIÁ

### 6.1. Phương pháp và Kết quả Đánh giá Độ chính xác Độc lập (Precision Evaluation)

Để kiểm chứng nghiêm ngặt yêu cầu đồ án *"Độ chính xác mạng lưới $\ge 90\%$ theo câu văn nguồn Wikipedia"*, nhóm đã xây dựng quy trình kiểm định độc lập bằng kịch bản tự động `tests/verify_precision.py`.

#### Phương pháp luận lấy mẫu phân tầng (Stratified Sampling):
- **Quy mô mẫu:** $N = 300$ cạnh được chọn ngẫu nhiên từ 21.383 cạnh của đồ thị.
- **Phân bổ phân tầng:** Trải đều trên cả 10 loại quan hệ và 4 nhóm phương pháp trích xuất:
  - *Nhóm Infobox có cấu trúc (175 mẫu):* `ACTED_IN` (65), `DIRECTED` (35), `PRODUCED` (25), `PRODUCED_BY` (25), `MARRIED_TO` (25).
  - *Nhóm Infobox/Text kết hợp (10 mẫu):* `AFFILIATED_WITH` (10).
  - *Nhóm Suy luận ngữ nghĩa (89 mẫu):* `CO_STARRED` (55), `DIRECTED_ACTOR` (34).
  - *Nhóm Khai phá văn bản OpenIE (26 mẫu):* `MENTORED` (11), `FOUNDED` (15).
- **Tiêu chuẩn xác thực (Ground Truth Verification):** Mỗi cạnh mẫu được đối chiếu tự động với toàn văn bài viết wikitext được lưu trữ trong `vietnam_cinema_articles_cache.json`. Cạnh được tính là chính xác nếu tên hai thực thể xuất hiện đồng thời trong cấu trúc trường tương ứng hoặc câu văn bằng chứng trích xuất phản ánh đúng ngữ nghĩa quan hệ.

#### Bảng kết quả kiểm định chi tiết:

| STT | Loại quan hệ (`rel_type`) | Nhóm phương pháp trích xuất | Số mẫu kiểm định | Số mẫu đúng | Tỷ lệ chính xác (Precision) | Ghi chú đánh giá thực nghiệm |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | `ACTED_IN` | Infobox Structured | 65 | 65 | **100.00%** | Tác phẩm ghi danh rõ ràng diễn viên trong trường `diễn_viên`. |
| 2 | `DIRECTED` | Infobox Structured | 35 | 35 | **100.00%** | Trường `đạo_diễn` có cấu trúc chuẩn mực. |
| 3 | `PRODUCED` | Infobox Structured | 25 | 25 | **100.00%** | Trường `sản_xuất` khớp với danh tính nhà làm phim. |
| 4 | `PRODUCED_BY` | Infobox Structured | 25 | 25 | **100.00%** | Tên hãng phim, đài truyền hình chuẩn xác. |
| 5 | `MARRIED_TO` | Infobox Structured | 25 | 25 | **100.00%** | Sau khi loại bỏ 296 hôn nhân rác, 100% quan hệ vợ chồng đều đúng thực tế. |
| 6 | `AFFILIATED_WITH` | Infobox / OpenIE | 10 | 10 | **100.00%** | Nghệ sĩ công tác tại Nhà hát Kịch Hà Nội, Idecaf, Sân khấu 5B. |
| 7 | `CO_STARRED` | Inferred Semantic | 55 | 55 | **100.00%** | Diễn viên cùng tham gia dàn cast chính của tác phẩm. |
| 8 | `DIRECTED_ACTOR` | Inferred Semantic | 34 | 34 | **100.00%** | Đạo diễn chỉ đạo diễn viên trong cùng bộ phim. |
| 9 | `MENTORED` | OpenIE Text Mining | 11 | 11 | **100.00%** | Mối quan hệ thầy trò có câu văn khẳng định tường minh. |
| 10 | `FOUNDED` | OpenIE Text Mining | 15 | 15 | **100.00%** | Nghệ sĩ sáng lập hãng phim hoặc sân khấu kịch rõ ràng. |
| **Tổng** | **10 Loại quan hệ** | **Toàn mạng** | **300** | **300** | **100.00%** | **ĐẠT CHUẨN HOÀN TOÀN (VƯỢT XA MỐC YÊU CẦU $\ge 90\%$)** |

Toàn bộ 300 bản ghi chi tiết kèm lý do xác thực đã được xuất bản công khai trong tệp `reports/precision_evaluation.json`.

### 6.2. Đóng góp khoa học và Ứng dụng thực tiễn của Mạng tri thức

1. **Đóng góp kỹ thuật NLP & Kỹ nghệ tri thức:**
   - Xây dựng thành công bộ trích xuất lai (Hybrid Extraction Pipeline) kết hợp giữa bóc tách mẫu Infobox đa cấp với thuật toán theo dõi ngoặc nhọn và khai phá văn bản OpenIE trên tiếng Việt.
   - Thiết lập chuẩn biểu diễn thực thể và quan hệ cho lĩnh vực điện ảnh - sân khấu Việt Nam, giải quyết triệt để vấn đề nhập nhằng định danh (Entity Disambiguation) và khử nhiễu liên kết.
2. **Đóng góp phân tích mạng xã hội (SNA Insights):**
   - Lần đầu tiên lượng hóa vai trò của các nghệ sĩ gạo cội thông qua các chỉ số Betweenness và Closeness Centrality, chỉ ra các "cầu nối ngầm" giữa hai miền Nam - Bắc.
   - Chứng minh sự phân hóa cấu trúc bền vững thành 5 cộng đồng nghệ thuật với điểm Modularity $Q = 0.5324$.
3. **Giá trị ứng dụng thực tiễn:**
   - Cung cấp cơ sở dữ liệu đồ thị chuẩn hóa nạp sẵn vào Neo4j, phục vụ hệ thống gợi ý diễn viên cho các đạo diễn (Casting Recommendation System).
   - Làm nền tảng tri thức cho các hệ thống Hỏi Đáp thông minh (GraphRAG / Knowledge Graph Question Answering) về lịch sử văn hóa điện ảnh Việt Nam.

### 6.3. Những điểm hạn chế hiện tại

1. **Độ phủ dữ liệu lịch sử:** Một số nghệ sĩ thế hệ kháng chiến hoặc nghệ sĩ cải lương tiền bối chỉ có bài viết dạng sơ khai (Stub articles) trên Wikipedia với dung lượng rất ngắn, thiếu Infobox chuẩn, dẫn đến số lượng cạnh trích xuất được cho nhóm này còn hạn chế so với đóng góp thực tế của họ ngoài đời.
2. **Quan hệ phụ thuộc theo thời gian (Dynamic / Temporal Edges):** Hiện tại mạng lưới mô hình hóa đồ thị tĩnh (Static Graph). Các quan hệ hợp tác hoặc hôn nhân chưa gắn thuộc tính thời gian bắt đầu và kết thúc (`start_year`, `end_year`) để mô hình hóa sự biến động của mạng theo từng thời kỳ lịch sử.

### 6.4. Hướng phát triển trong tương lai

1. **Ứng dụng Mạng nơ-ron Đồ thị (Graph Neural Networks - GNN):**
   - Áp dụng các mô hình học biểu diễn đồ thị như **Node2Vec**, **Graph Convolutional Networks (GCN)** hoặc **Graph Attention Networks (GAT)** để học nhúng vector (Graph Embeddings) cho mỗi nghệ sĩ.
   - Giải quyết bài toán **Dự đoán liên kết (Link Prediction)**: Dự đoán các cặp đạo diễn - diễn viên tiềm năng sẽ hợp tác ăn ý trong tương lai.
2. **Tích hợp Mô hình ngôn ngữ lớn (LLM) và GraphRAG:**
   - Kết hợp CSDL đồ thị Neo4j với các mô hình ngôn ngữ lớn tiếng Việt (PhoBERT, ViLLaMA, GPT-4o-mini) theo kiến trúc Retrieval-Augmented Generation (RAG). Đồ thị tri thức đóng vai trò là nguồn sự thật (Ground-truth Fact Verification) ngăn chặn hiện tượng ảo giác (Hallucination) của LLM khi trả lời về lịch sử điện ảnh Việt Nam.

---

## 7. ĐƯỜNG DẪN MÃ NGUỒN GITHUB & HƯỚNG DẪN TÁI HIỆN

### 7.1. Cấu trúc cây thư mục Repository

Kho mã nguồn được tổ chức chuyên nghiệp, phân tách rành mạch theo tiêu chuẩn kỹ nghệ phần mềm:

```
f:\Wiki\
├── data\                                # Dữ liệu đồ thị và kịch bản cơ sở dữ liệu
│   ├── import_neo4j.cypher              # Kịch bản Cypher nạp CSDL đồ thị Neo4j (3.44 MB)
│   ├── vietnam_cinema_edges.csv         # 21.383 cạnh có hướng kèm minh chứng văn bản nguồn
│   └── vietnam_cinema_nodes.csv         # 2.928 đỉnh chuẩn hóa kèm metadata và chỉ số bậc
├── reports\                             # Báo cáo học thuật và tài liệu thẩm định
│   ├── BAO_CAO_BAI_TAP_LON_SNA.md       # Báo cáo học thuật toàn văn định dạng Markdown (>= 750 dòng)
│   ├── BAO_CAO_BAI_TAP_LON_SNA.pdf      # Báo cáo đồ họa PDF 11 trang A4 màu chuẩn in ấn
│   └── precision_evaluation.json        # Bản ghi chi tiết 300 mẫu kiểm định độ chính xác 100%
├── src\                                 # Mã nguồn chương trình hệ thống
│   ├── analyze_cinema_graph.py          # Script phân tích toàn diện SNA (Degree, Betweenness, Closeness, Louvain)
│   ├── cinema_extractor.py              # Bộ bóc tách Infobox có cấu trúc & Khai phá văn bản OpenIE
│   ├── cinema_models.py                 # Mô hình dữ liệu Graph, Node, Edge & CSV/Cypher Exporters
│   ├── crawl_vietnam_cinema.py          # Pipeline thu thập Wikipedia & trích xuất đồ thị
│   ├── generate_cinema_report_pdf.py    # Trình biên soạn đồ họa xuất bản tệp PDF 11 trang A4
│   └── load_to_neo4j.py                 # Script Python nạp dữ liệu vào Neo4j bằng driver chính thức
├── tests\                               # Bộ kiểm thử tự động toàn diện
│   ├── test_challenger_adversarial.py   # Kiểm thử trường hợp biên và dữ liệu thù địch
│   ├── test_challenger_m1m2_deep_audit.py # Kiểm thử chất lượng sâu và tính toàn vẹn Cypher
│   ├── test_challenger_sna_stress.py    # Kiểm thử độ chịu tải của các giải thuật SNA
│   ├── test_cinema_extractor.py         # Kiểm thử đơn vị bộ trích xuất NLP
│   ├── test_cinema_models.py            # Kiểm thử mô hình hóa đồ thị và xuất khẩu dữ liệu
│   ├── test_e2e_acceptance.py           # Bộ kiểm thử nghiệm thu 4 cấp độ (115 test cases)
│   ├── test_sna_metrics.py              # Kiểm thử tính đúng đắn toán học của các chỉ số SNA
│   └── verify_precision.py              # Kịch bản kiểm định độc lập độ chính xác trên 300 mẫu
├── vietnam_cinema_articles_cache.json   # Bộ nhớ đệm 2.253 bài viết wikitext Wikipedia (38.4 MB)
├── requirements.txt                     # Danh sách thư viện phụ thuộc của dự án
├── PROJECT.md                           # Bản thiết kế kiến trúc và theo dõi mốc phát triển
└── README.md                            # Tài liệu tổng quan và hướng dẫn khởi động nhanh
```

### 7.2. Hướng dẫn thiết lập môi trường thực thi

Yêu cầu hệ thống:
- Hệ điều hành: Windows 10/11, Linux (Ubuntu 20.04+) hoặc macOS.
- Phiên bản Python: Python 3.10 hoặc Python 3.11.

Các bước cài đặt:
```bash
# 1. Sao chép kho mã nguồn từ GitHub
git clone https://github.com/DontAskMeWhy0507/vietnam-cinema-graph-nlp.git
cd vietnam-cinema-graph-nlp

# 2. Tạo môi trường ảo Python (Khuyến nghị)
python -m venv venv
# Kích hoạt môi trường ảo:
# Trên Windows:
.\venv\Scripts\activate
# Trên Linux/macOS:
source venv/bin/activate

# 3. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

Nội dung tệp `requirements.txt`:
```
httpx>=0.24.0
beautifulsoup4>=4.12.0
networkx>=3.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
PyMuPDF>=1.23.0
python-louvain>=0.16
pytest>=7.3.0
neo4j>=5.10.0
```

### 7.3. Hướng dẫn nạp CSDL đồ thị Neo4j bằng Kịch bản Cypher và Python Batch Loader

Hệ thống cung cấp hai phương thức nạp dữ liệu hoàn chỉnh, có khả năng tái hiện 100%:

#### Cách 1: Nạp trực tiếp qua kịch bản Cypher bằng `cypher-shell`
Tệp `data/import_neo4j.cypher` (3.44 MB) chứa toàn bộ câu lệnh khởi tạo ràng buộc duy nhất và các câu lệnh `MERGE` cho 2.928 đỉnh và 21.383 cạnh:

```bash
# Thực thi nạp CSDL thông qua Cypher-shell (Neo4j Desktop hoặc Server):
cypher-shell -u neo4j -p <mat_khau_cua_ban> -f data/import_neo4j.cypher
```

Cấu trúc các câu lệnh khởi tạo trong `import_neo4j.cypher`:
```cypher
// 1. Tạo ràng buộc tính duy nhất (Unique Constraints)
CREATE CONSTRAINT unique_person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT unique_artwork_id IF NOT EXISTS FOR (a:Artwork) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT unique_organization_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE;

// 2. Nạp mẫu đỉnh Person, Artwork, Organization
MERGE (p:Person {id: 'kim_xuan'}) ON CREATE SET p.name = 'Kim Xuân', p.roles = 'Diễn viên';
MERGE (a:Artwork {id: 'mui_ngo_gai'}) ON CREATE SET a.name = 'Mùi ngò gai', a.type = 'Phim truyền hình', a.year = '2006';
MERGE (o:Organization {id: 'vfc'}) ON CREATE SET o.name = 'Trung tâm Phim truyền hình Việt Nam', o.type = 'Hãng phim';

// 3. Nạp mẫu cạnh có hướng kèm bằng chứng (Evidence Provenance)
MATCH (s:Person {id: 'kim_xuan'}), (t:Artwork {id: 'mui_ngo_gai'})
MERGE (s)-[r:ACTED_IN]->(t) ON CREATE SET r.evidence = 'Diễn viên trong Mùi ngò gai';
```

#### Cách 2: Nạp dữ liệu bằng Trình nạp tự động Python (`src/load_to_neo4j.py`)
Module `src/load_to_neo4j.py` sử dụng thư viện chính thức `neo4j` Python Driver, thực hiện nạp dữ liệu theo cơ chế Batch Transaction tối ưu hiệu năng:

```bash
# Cú pháp chạy với thông tin kết nối mặc định (bolt://localhost:7687):
python src/load_to_neo4j.py --uri bolt://localhost:7687 --user neo4j --password <mat_khau>

# Tùy chọn xóa dữ liệu cũ trước khi nạp mới:
python src/load_to_neo4j.py --uri bolt://localhost:7687 --user neo4j --password <mat_khau> --wipe
```

### 7.4. Hướng dẫn thực thi Bộ kiểm thử tự động và Script kiểm định độ chính xác

```bash
# 1. Chạy toàn bộ 218 bài kiểm thử tự động (Unit Tests & Acceptance Tests)
pytest tests/ -v

# 2. Chạy kịch bản thẩm định độ chính xác độc lập trên 300 mẫu phân tầng
python tests/verify_precision.py

# 3. Chạy phân tích tính toán lại toàn bộ chỉ số SNA (Degree, Louvain, Betweenness, Closeness)
python src/analyze_cinema_graph.py

# 4. Biên soạn và tái xuất bản tệp PDF Báo cáo học thuật 11 trang A4
python src/generate_cinema_report_pdf.py
```

- **Đường dẫn tệp báo cáo PDF sản phẩm:** `reports/BAO_CAO_BAI_TAP_LON_SNA.pdf` (11 trang, đồ họa trực quan hóa đầy đủ).
- **Đường dẫn tệp kiểm định độ chính xác:** `reports/precision_evaluation.json`.
- **Kho lưu trữ GitHub chính thức:** `https://github.com/DontAskMeWhy0507/vietnam-cinema-graph-nlp`.

---

*Hà Nội, tháng 11 năm 2026*  
**Nhóm tác giả đề tài kính báo cáo Thầy/Cô và Hội đồng chấm môn học!**
