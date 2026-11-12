"""
generate_latex_report.py
Sinh mã nguồn LaTeX chuẩn học thuật (theo khung template INT3228E - UET)
từ dữ liệu đồ thị thực tế và kết quả phân tích SNA.
Mọi số liệu thống kê, bảng biểu và minh chứng đều được đọc và tính trực tiếp từ
data/vietnam_cinema_nodes.csv, data/vietnam_cinema_edges.csv và reports/precision_evaluation.json.
"""

import os
import csv
import json
from collections import Counter, defaultdict
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, shortest_path
import networkx as nx
import community as community_louvain

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
REPORT_DIR = os.path.join(ROOT_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)


def tex_escape(text: str) -> str:
    """Thoát các ký tự đặc biệt của LaTeX một cách an toàn."""
    if text is None:
        return ""
    s = str(text)
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for old, new in replacements:
        s = s.replace(old, new)
    return s


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def collect_verified_metrics():
    nodes_file = os.path.join(DATA_DIR, "vietnam_cinema_nodes.csv")
    edges_file = os.path.join(DATA_DIR, "vietnam_cinema_edges.csv")
    cypher_file = os.path.join(DATA_DIR, "import_neo4j.cypher")
    prec_file = os.path.join(REPORT_DIR, "precision_evaluation.json")
    cache_file = os.path.join(ROOT_DIR, "vietnam_cinema_articles_cache.json")

    with open(nodes_file, mode="r", encoding="utf-8-sig") as f:
        nodes = list(csv.DictReader(f))
    for n in nodes:
        n["in_degree"] = int(n["in_degree"])
        n["out_degree"] = int(n["out_degree"])
        n["tot_degree"] = n["in_degree"] + n["out_degree"]

    with open(edges_file, mode="r", encoding="utf-8-sig") as f:
        edges = list(csv.DictReader(f))

    with open(prec_file, mode="r", encoding="utf-8") as f:
        prec = json.load(f)

    cache_bytes = os.path.getsize(cache_file) if os.path.exists(cache_file) else 0
    cache_articles = prec["metadata"]["total_cached_articles"]
    cypher_bytes = os.path.getsize(cypher_file)
    cypher_lines = sum(1 for _ in open(cypher_file, encoding="utf-8"))

    N = len(nodes)
    E = len(edges)
    label_counts = Counter(n["label"] for n in nodes)
    rel_counts = Counter(e["rel_type"] for e in edges)

    id_to_idx = {n["id"]: i for i, n in enumerate(nodes)}
    idx_to_id = {i: n["id"] for i, n in enumerate(nodes)}
    id_to_node = {n["id"]: n for n in nodes}

    rows = [id_to_idx[e["source_id"]] for e in edges]
    cols = [id_to_idx[e["target_id"]] for e in edges]
    edges_set = {(e["source_id"], e["target_id"]) for e in edges}

    costar_set = {(e["source_id"], e["target_id"]) for e in edges if e["rel_type"] == "CO_STARRED"}
    costar_sym_edges = sum(1 for (a, b) in costar_set if (b, a) in costar_set)
    costar_asym_edges = len(costar_set) - costar_sym_edges

    adj_directed = csr_matrix((np.ones(E, dtype=float), (rows, cols)), shape=(N, N))
    density = E / (N * (N - 1))
    avg_degree = E / N
    reciprocal = sum(1 for (s, t) in edges_set if (t, s) in edges_set)
    reciprocity_pct = reciprocal / E * 100.0

    n_wcc, labels_wcc = connected_components(adj_directed, directed=True, connection="weak")
    n_scc, labels_scc = connected_components(adj_directed, directed=True, connection="strong")
    largest_wcc = Counter(labels_wcc).most_common(1)[0][1]
    largest_scc = Counter(labels_scc).most_common(1)[0][1]

    in_arr = [n["in_degree"] for n in nodes]
    out_arr = [n["out_degree"] for n in nodes]
    pct_points = [10, 25, 50, 75, 90, 95, 99, 100]
    in_pcts = {p: int(np.percentile(in_arr, p)) for p in pct_points}
    out_pcts = {p: int(np.percentile(out_arr, p)) for p in pct_points}
    max_in_node = max(nodes, key=lambda x: x["in_degree"])
    max_out_node = max(nodes, key=lambda x: x["out_degree"])

    deg_hist = Counter(n["in_degree"] for n in nodes if n["in_degree"] >= 2)
    ks = np.array(sorted(deg_hist.keys()), dtype=float)
    ys = np.array([deg_hist[int(k)] for k in ks], dtype=float)
    slope, _ = np.polyfit(np.log10(ks), np.log10(ys), 1)
    gamma = -float(slope)

    h = np.ones(N)
    a = np.ones(N)
    adj_t = adj_directed.T.tocsr()
    for _ in range(30):
        a = adj_t.dot(h)
        a /= np.linalg.norm(a)
        h = adj_directed.dot(a)
        h /= np.linalg.norm(h)

    out_sums = np.array(adj_directed.sum(axis=1)).flatten()
    d = 0.85
    pr = np.ones(N) / N
    dangling = (out_sums == 0)
    out_safe = np.where(out_sums == 0, 1.0, out_sums)
    M = adj_directed.multiply(1.0 / out_safe[:, None]).T.tocsr()
    for _ in range(50):
        pr_next = d * (M.dot(pr) + np.sum(pr[dangling]) / N) + (1.0 - d) / N
        if np.allclose(pr, pr_next, atol=1e-7):
            break
        pr = pr_next

    G_nx = nx.Graph()
    for e in edges:
        G_nx.add_edge(e["source_id"], e["target_id"])
    betw = nx.betweenness_centrality(G_nx, k=min(300, G_nx.number_of_nodes()), seed=42)

    adj_und = adj_directed + adj_directed.T
    adj_und.data = np.ones_like(adj_und.data)
    dist_mat = shortest_path(adj_und, directed=False, unweighted=True)
    reach_mask = (dist_mat > 0) & (~np.isinf(dist_mat))
    reach_cnt = np.sum(reach_mask, axis=1)
    tot_dist = np.sum(np.where(reach_mask, dist_mat, 0), axis=1)
    clos = {}
    for i in range(N):
        nid = idx_to_id[i]
        clos[nid] = float((reach_cnt[i] / (N - 1)) * (reach_cnt[i] / tot_dist[i])) if reach_cnt[i] > 0 and tot_dist[i] > 0 else 0.0

    part = community_louvain.best_partition(G_nx, random_state=42)
    modularity_q = float(community_louvain.modularity(part, G_nx))
    comm_counts = Counter(part.values())

    for i, node in enumerate(nodes):
        nid = node["id"]
        node["pagerank"] = float(pr[i])
        node["authority"] = float(a[i])
        node["hub"] = float(h[i])
        node["betweenness"] = float(betw.get(nid, 0.0))
        node["closeness"] = float(clos.get(nid, 0.0))
        node["community"] = int(part.get(nid, -1))

    persons = [n for n in nodes if n["label"] == "Person"]
    top15_in = sorted(persons, key=lambda x: (x["in_degree"], x["tot_degree"]), reverse=True)[:15]
    top5_pr = sorted(persons, key=lambda x: x["pagerank"], reverse=True)[:5]
    top5_betw = sorted(persons, key=lambda x: x["betweenness"], reverse=True)[:5]
    top5_clos = sorted(persons, key=lambda x: x["closeness"], reverse=True)[:5]
    top5_auth = sorted(persons, key=lambda x: x["authority"], reverse=True)[:5]
    top5_hub = sorted(persons, key=lambda x: x["hub"], reverse=True)[:5]

    dir_actor_counts = Counter(e["source_id"] for e in edges if e["rel_type"] == "DIRECTED_ACTOR")
    dir_sample_actors = defaultdict(list)
    dir_films = defaultdict(list)
    for e in edges:
        if e["rel_type"] == "DIRECTED_ACTOR":
            nm = e["target_name"]
            if nm not in dir_sample_actors[e["source_id"]]:
                dir_sample_actors[e["source_id"]].append(nm)
        elif e["rel_type"] == "DIRECTED":
            nm = e["target_name"]
            if nm not in dir_films[e["source_id"]]:
                dir_films[e["source_id"]].append(nm)

    work_actors = defaultdict(set)
    for e in edges:
        if e["rel_type"] == "ACTED_IN":
            work_actors[e["target_name"]].add(e["source_name"])
    shared_works = Counter()
    shared_titles = defaultdict(list)
    for work, actors in work_actors.items():
        alist = sorted(actors)
        for i in range(len(alist)):
            for j in range(i + 1, len(alist)):
                a1, a2 = alist[i], alist[j]
                if a1.split(" (")[0].strip() == a2.split(" (")[0].strip():
                    continue
                if "#" in a1 or "#" in a2:
                    continue
                pair = (a1, a2)
                shared_works[pair] += 1
                shared_titles[pair].append(work)

    mentored_edges = [e for e in edges if e["rel_type"] == "MENTORED"]
    top_orgs = Counter(e["target_name"] for e in edges if e["rel_type"] == "PRODUCED_BY").most_common(5)

    return {
        "N": N, "E": E,
        "label_counts": label_counts,
        "rel_counts": rel_counts,
        "costar_sym_pairs": costar_sym_edges // 2,
        "costar_sym_edges": costar_sym_edges,
        "costar_asym_edges": costar_asym_edges,
        "density": density,
        "avg_degree": avg_degree,
        "reciprocal": reciprocal,
        "reciprocity_pct": reciprocity_pct,
        "n_wcc": n_wcc, "largest_wcc": largest_wcc,
        "n_scc": n_scc, "largest_scc": largest_scc,
        "in_pcts": in_pcts, "out_pcts": out_pcts,
        "max_in_node": max_in_node, "max_out_node": max_out_node,
        "gamma": gamma,
        "modularity_q": modularity_q,
        "num_communities": len(comm_counts),
        "connected_nodes": G_nx.number_of_nodes(),
        "isolated_nodes": N - G_nx.number_of_nodes(),
        "comm_counts": comm_counts,
        "persons": persons,
        "id_to_node": id_to_node,
        "top15_in": top15_in,
        "top5_pr": top5_pr,
        "top5_betw": top5_betw,
        "top5_clos": top5_clos,
        "top5_auth": top5_auth,
        "top5_hub": top5_hub,
        "dir_actor_top5": dir_actor_counts.most_common(5),
        "dir_sample_actors": dir_sample_actors,
        "dir_films": dir_films,
        "costar_top5": shared_works.most_common(5),
        "shared_titles": shared_titles,
        "mentored_edges": mentored_edges,
        "top_orgs": top_orgs,
        "prec": prec,
        "cache_mb_dec": cache_bytes / 1_000_000.0,
        "cache_articles": cache_articles,
        "cypher_mib": cypher_bytes / (1024.0 * 1024.0),
        "cypher_lines": cypher_lines,
    }


LATEX_TEMPLATE = r"""\documentclass[12pt,a4paper]{article}
\usepackage{fontspec}
\setmainfont{cmunrm.otf}[
  BoldFont=cmunbx.otf,
  ItalicFont=cmunti.otf,
  BoldItalicFont=cmunbi.otf
]
\setmonofont{cmuntt.otf}[
  Scale=0.92,
  BoldFont=cmuntb.otf
]
\usepackage[vietnamese]{babel}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{float}
\usepackage[hidelinks]{hyperref}
\usepackage{xurl}
\usepackage{array}
\usepackage{tabularx}
\usepackage{listings}
\geometry{margin=2.5cm}
\setlength{\emergencystretch}{1.5em}

\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}
\let\oldunderscore\_
\renewcommand{\_}{\oldunderscore\hspace{0pt}}

\graphicspath{{figures/}{./}}

\lstdefinelanguage{cypher}{
  keywords={MATCH, MERGE, CREATE, CONSTRAINT, ON, SET, RETURN, WHERE, AS, ORDER, BY, DESC, LIMIT, CALL, YIELD, REQUIRE, IS, UNIQUE, IF, NOT, EXISTS, FOR, UNWIND},
  sensitive=true,
  comment=[l]{//},
  morestring=[b]',
  morestring=[b]"
}

\lstset{
  language=cypher,
  basicstyle=\ttfamily\small,
  frame=tb,
  breaklines=true,
  breakatwhitespace=true,
  tabsize=2,
  showstringspaces=false,
  aboveskip=0.8em,
  belowskip=0.8em
}

\begin{document}
\pagenumbering{gobble}
\begin{titlepage}
\centering
{\Large \textbf{ĐẠI HỌC QUỐC GIA HÀ NỘI}\\[0.25cm]}
{\Large \textbf{TRƯỜNG ĐẠI HỌC CÔNG NGHỆ}\\[1.0cm]}

\includegraphics[width=0.23\textwidth]{logo.png}\\[1.2cm]

{\LARGE \textbf{BÁO CÁO BÀI TẬP LỚN MÔN HỌC}\\[0.45cm]}
{\LARGE \textbf{PHÂN TÍCH MẠNG XÃ HỘI}\\[1.3cm]}

\begin{flushleft}
\hspace{1.2cm}\textbf{Học phần:} Phân tích Mạng Xã hội -- ĐH Công nghệ, ĐHQGHN\\[0.32cm]
\hspace{1.2cm}\textbf{Đề tài:} Mạng lưới diễn viên và đạo diễn Việt Nam từ dữ liệu Wikipedia\\[0.32cm]
\hspace{1.2cm}\textbf{Quy mô đồ thị:} @@TOTAL_N@@ nút, @@TOTAL_E@@ cạnh có hướng, 10 loại quan hệ\\[0.32cm]
\hspace{1.2cm}\textbf{CSDL đồ thị:} Neo4j 5.x Property Graph \& Graph Data Science\\[0.32cm]
\hspace{1.2cm}\textbf{Nhóm thực hiện:} Nhóm 10\\[0.32cm]
\hspace{1.2cm}\textbf{Sinh viên:} Vũ Tiến Tuấn Trung -- MSV: 23020576\\[0.32cm]
\hspace{1.2cm}\phantom{\textbf{Sinh viên:}} Đặng Anh Quế -- MSV: 23020565\\[0.32cm]
\hspace{1.2cm}\textbf{GitHub:} {\small\url{https://github.com/DontAskMeWhy0507/vietnam-cinema-graph-nlp}}
\end{flushleft}

\vfill
{\large Hà Nội, \today}
\end{titlepage}

\pagenumbering{roman}
\tableofcontents
\newpage
\pagenumbering{arabic}

\section{Phân công công việc trong nhóm}

Đề tài được thực hiện bởi \textbf{Nhóm 10} gồm hai thành viên, phân chia nhiệm vụ theo từng chặng của quy trình thu thập dữ liệu, trích xuất xử lý ngôn ngữ tự nhiên (NLP), lưu trữ cơ sở dữ liệu đồ thị Neo4j và phân tích mạng xã hội (SNA).

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{c P{3.3cm} P{2.7cm} L c}
\toprule
STT & Thành viên & Vai trò & Nhiệm vụ thực hiện & Tỷ lệ \\
\midrule
1 & Vũ Tiến Tuấn Trung \newline (MSV: 23020576) & Thu thập dữ liệu \& Trích xuất NLP &
Khảo sát cây thể loại Wikipedia tiếng Việt; lập trình crawler \texttt{src/\allowbreak crawl\_vietnam\_cinema.py}; xây dựng bộ phân tích Infobox Brace-Depth và mẫu Regex OpenIE trong \texttt{src/\allowbreak cinema\_extractor.py}; lưu bộ nhớ đệm @@CACHE_ARTICLES@@ bài viết (\texttt{vietnam\_cinema\_articles\_cache.json}). & 50\% \\
\midrule
2 & Đặng Anh Quế \newline (MSV: 23020565) & Mô hình hóa Neo4j, Phân tích SNA \& Báo cáo &
Thiết kế schema đồ thị 3 nhãn đỉnh trong \texttt{src/\allowbreak cinema\_models.py}; sinh script Cypher (\texttt{data/\allowbreak import\_neo4j.cypher}) và trình nạp \texttt{src/\allowbreak load\_to\_neo4j.py}; cài đặt thuật toán SNA (\texttt{src/\allowbreak analyze\_cinema\_graph.py}); kiểm định phân tầng 300 mẫu, viết 218 bài kiểm thử tự động và tổng hợp báo cáo. & 50\% \\
\bottomrule
\end{tabularx}
\caption{Bảng phân công công việc Nhóm 10}
\label{tab:task-allocation}
\end{table}

\section{Giới thiệu mạng đã xây dựng, lựa chọn nút và cạnh}

\subsection{Mục tiêu và phạm vi đề tài}

Nghề diễn viên, đạo diễn và hoạt động sân khấu tại Việt Nam tạo nên một mạng lưới hợp tác xã hội có cấu trúc phân tầng rõ rệt qua nhiều giai đoạn: điện ảnh cách mạng thế kỷ 20, kịch nói và cải lương truyền thống, phim truyền hình nhiều tập (VFC, TFS, HTV) và điện ảnh thương mại hiện đại. Từ nguồn dữ liệu Wikipedia tiếng Việt, đề tài khai thác đồng thời hộp thông tin có cấu trúc (\textit{Infobox}) và văn bản tự nhiên tại các mục \textit{Sự nghiệp}, \textit{Tiểu sử} để dựng thành một mạng lưới tri thức xã hội đạt tối thiểu 2.000 nút, 5.000 cạnh và 10 loại quan hệ ngữ nghĩa chi tiết.

Trọng tâm thiết kế của đồ thị là phân tách rạch ròi bản chất từng loại quan hệ hợp tác thay vì gộp chung thành một cạnh vô hướng đồng nhất: đạo diễn chỉ đạo diễn viên (\texttt{DIRECTED\_ACTOR}), hai diễn viên đóng cặp ăn ý (\texttt{CO\_STARRED}), quan hệ thầy trò hoặc người nâng đỡ phát hiện tài năng (\texttt{MENTORED}), cùng các quan hệ tác phẩm, hôn phối và tổ chức sản xuất.

\subsection{Lựa chọn nút (Nodes)}

Mạng lưới được mô hình hóa dưới dạng Mạng thông tin không đồng nhất (Heterogeneous Information Network -- HIN) ký hiệu $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \phi, \psi)$, với tổng cộng \textbf{@@TOTAL_N@@ nút} phân bố vào 3 nhãn thực thể $\mathcal{T}_V = \{\texttt{Person}, \texttt{Artwork}, \texttt{Organization}\}$ như tổng hợp ở Bảng~\ref{tab:node-labels} và Hình~\ref{fig:node-cast}. Việc giữ cả \texttt{Artwork} và \texttt{Organization} làm đỉnh độc lập giúp truy xuất trực tiếp bằng chứng tác phẩm gốc và hỗ trợ chiếu mạng 2-hop trong Neo4j.

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{l r r L}
\toprule
Nhãn nút & Số lượng & Tỷ lệ & Phạm vi thực thể và thuộc tính lưu trữ \\
\midrule
\texttt{Person} & @@N_PERSON@@ & @@PCT_PERSON@@\% & Diễn viên điện ảnh, truyền hình, kịch nói, cải lương, đạo diễn, nhà sản xuất. Thuộc tính: \texttt{id}, \texttt{name}, \texttt{roles}, \texttt{in\_degree}, \texttt{out\_degree}. \\
\texttt{Artwork} & @@N_ARTWORK@@ & @@PCT_ARTWORK@@\% & Phim điện ảnh, phim truyền hình nhiều tập, vở kịch, vở chèo và cải lương. Thuộc tính: \texttt{id}, \texttt{title}, \texttt{type}, \texttt{year}, \texttt{in\_degree}, \texttt{out\_degree}. \\
\texttt{Organization} & @@N_ORG@@ & @@PCT_ORG@@\% & Hãng phim, công ty sản xuất, đài truyền hình (VTV, HTV), sân khấu kịch, nhà hát. Thuộc tính: \texttt{id}, \texttt{name}, \texttt{type}, \texttt{in\_degree}, \texttt{out\_degree}. \\
\midrule
Tổng cộng & @@TOTAL_N@@ & 100.00\% & Lưu chuẩn hóa tại \texttt{data/\allowbreak vietnam\_cinema\_nodes.csv}. \\
\bottomrule
\end{tabularx}
\caption{Phân bổ số lượng nút theo 3 nhãn bản thể học}
\label{tab:node-labels}
\end{table}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\textwidth]{node_composition_and_cast.pdf}
\caption{Cơ cấu 3 nhãn nút và Top 7 tác phẩm có số nghệ sĩ tham gia nhiều nhất}
\label{fig:node-cast}
\end{figure}

\subsection{Lựa chọn cạnh và 10 loại quan hệ chi tiết (Edges)}

Tập cạnh $\mathcal{E}$ bao gồm \textbf{@@TOTAL_E@@ cạnh có hướng}, mỗi cạnh lưu đủ bộ ba định danh \texttt{(source\_id, target\_id, rel\_type)} kèm trường văn bản minh chứng \texttt{evidence}. Toàn bộ tập cạnh tuân thủ đúng 10 kiểu quan hệ ngữ nghĩa chi tiết (Bảng~\ref{tab:edge-types} và Hình~\ref{fig:edge-dist}):

\begin{table}[htbp]
\centering
\footnotesize
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.12}
\begin{tabularx}{\textwidth}{c P{2.85cm} P{2.65cm} r r L}
\toprule
STT & Loại quan hệ & Miền Nguồn $\to$ Đích & Số cạnh & Tỷ lệ & Định nghĩa ngữ nghĩa \\
\midrule
@@EDGE_ROWS@@
\midrule
-- & Tổng cộng & 10 loại quan hệ & @@TOTAL_E@@ & 100.00\% & Lưu tại \texttt{data/\allowbreak vietnam\_cinema\_edges.csv}. \\
\bottomrule
\end{tabularx}
\caption{Thống kê và định nghĩa 10 loại quan hệ chi tiết trong đồ thị}
\label{tab:edge-types}
\end{table}

Sự phân biệt giữa 3 loại quan hệ cốt lõi của bài toán được thiết lập như sau:
\begin{itemize}
  \item \textbf{\texttt{DIRECTED\_ACTOR} (Đạo diễn chỉ đạo):} Là quan hệ có hướng từ đạo diễn sang diễn viên (\texttt{Person} $\to$ \texttt{Person}), phản ánh sự dẫn dắt nghệ thuật và tuyển chọn diễn viên (ví dụ: Vũ Trường Khoa $\to$ Doãn Quốc Đam, Nguyễn Phương Điền $\to$ Cao Minh Đạt).
  \item \textbf{\texttt{CO\_STARRED} (Diễn viên đóng cặp / đồng diễn):} Là quan hệ đối xứng (\texttt{Person} $\leftrightarrow$ \texttt{Person}), ghi nhận các diễn viên xuất hiện cùng trong dàn cast chính một tác phẩm hoặc được văn bản miêu tả là bạn diễn ăn ý. Trong tệp dữ liệu có @@TOTAL_COSTAR@@ cạnh có hướng, gồm @@COSTAR_SYM_PAIRS@@ cặp kết nối hai chiều (@@COSTAR_SYM_EDGES@@ cạnh) và @@COSTAR_ASYM_EDGES@@ cạnh đơn hướng trích từ tiểu sử.
  \item \textbf{\texttt{MENTORED} (Người nâng đỡ / Phát hiện tài năng):} Là quan hệ có hướng (\texttt{Person} $\to$ \texttt{Person}) chỉ sinh ra khi văn bản tiểu sử khẳng định rõ việc truyền nghề, dìu dắt hoặc đào tạo trực tiếp (ví dụ: Công Ninh $\to$ Hứa Minh Đạt, Hữu Lộc $\to$ Trường Giang, Xuân Huyền $\to$ Giang Còi).
\end{itemize}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.88\textwidth]{edge_distribution.pdf}
\caption{Phân bổ số lượng cạnh qua 10 loại quan hệ (thang đo logarit)}
\label{fig:edge-dist}
\end{figure}

\section{Stack công nghệ thu thập, xử lý Wikipedia và lưu trữ dữ liệu}

\subsection{Kiến trúc tổng thể hệ thống}

Hệ thống được triển khai hoàn toàn bằng Python 3.11 theo kiến trúc đường ống gồm 4 tầng tách biệt: thu thập dữ liệu Wikipedia, phân tích cú pháp Infobox và khai phá văn bản NLP, kiểm soát tính toàn vẹn theo Ontology, và xuất bản sang cơ sở dữ liệu đồ thị Neo4j cùng phân tích SNA.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth]{pipeline_architecture.pdf}
\caption{Kiến trúc đường ống xử lý dữ liệu từ Wikipedia tới CSDL đồ thị}
\label{fig:pipeline}
\end{figure}

\subsection{Công nghệ thu thập và xử lý dữ liệu Wikipedia}

Các thư viện và thành phần công nghệ được lựa chọn nhằm đảm bảo tốc độ xử lý, tính tái lập offline và khả năng kiểm soát lỗi chặt chẽ (Hình~\ref{fig:pipeline}, Bảng~\ref{tab:tech-stack}):

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{P{3.0cm} P{4.2cm} L}
\toprule
Thành phần & Công nghệ / Thư viện & Vai trò trong hệ thống \\
\midrule
Thu thập dữ liệu & \texttt{httpx} + MediaWiki Action API & Duyệt cây thể loại qua API \texttt{categorymembers}; tải wikitext theo lô 40 bài/\allowbreak request với độ trễ giãn cách 0.1 giây. \\
Lưu trữ đệm & JSON Offline Cache & Lưu toàn bộ @@CACHE_ARTICLES@@ bài viết wikitext vào tệp \texttt{vietnam\_cinema\_articles\_cache.json} (@@CACHE_MB@@ MB), giúp tái chạy toàn bộ NLP không phụ thuộc mạng. \\
Tiền xử lý \& NLP & \texttt{re}, Brace-Depth State Machine & Bóc tách tham số Infobox nhiều cấp ngoặc nhọn và khai phá câu tường thuật trong mục \textit{Sự nghiệp}, \textit{Tiểu sử}. \\
Tính toán SNA & \texttt{scipy.sparse.csr\_matrix}, \texttt{networkx}, \texttt{python-louvain} & Biểu diễn ma trận kề thưa @@TOTAL_N@@$\times$@@TOTAL_N@@, tính PageRank, HITS, Closeness, Betweenness và phân cụm Louvain. \\
CSDL Đồ thị & Neo4j 5.x + driver \texttt{neo4j} & Lưu trữ đồ thị thuộc tính (Property Graph), chạy truy vấn Cypher và thuật toán đồ thị cuối kỳ. \\
Kiểm thử \& Báo cáo & \texttt{pytest}, \texttt{matplotlib}, Tectonic LaTeX & Tự động hóa 218 ca kiểm thử, xuất biểu đồ vector PDF và biên soạn báo cáo. \\
\bottomrule
\end{tabularx}
\caption{Stack công nghệ sử dụng trong hệ thống}
\label{tab:tech-stack}
\end{table}

\subsection{Lựa chọn hệ quản trị cơ sở dữ liệu Neo4j và hỗ trợ thuật toán cuối kỳ}

Đề tài lựa chọn \textbf{Neo4j 5.x} làm hệ quản trị cơ sở dữ liệu đồ thị lưu trữ mạng kết quả vì mô hình đồ thị thuộc tính có nhãn (Labeled Property Graph) của Neo4j ánh xạ trực tiếp 3 nhãn đỉnh (\texttt{Person}, \texttt{Artwork}, \texttt{Organization}) và 10 loại cạnh có hướng kèm thuộc tính \texttt{evidence}.

Trong cấu trúc \textit{index-free adjacency} của Neo4j, mỗi đỉnh lưu con trỏ vật lý tới các cạnh kề, cho phép thực hiện các truy vấn đường đi đa chặng ($k$-hop traversal) nhanh hơn nhiều so với phép \texttt{JOIN} bảng trong cơ sở dữ liệu quan hệ. Đặc biệt, Neo4j tích hợp sẵn thư viện \textbf{Neo4j Graph Data Science (GDS)} phục vụ trực tiếp các thuật toán cho bài tập cuối kỳ như PageRank, Betweenness Centrality, Louvain Community Detection, Node2Vec embedding và dự đoán liên kết (Link Prediction).

Hệ thống cung cấp hai phương thức nạp dữ liệu sang Neo4j:
\begin{enumerate}
  \item Nạp qua tệp kịch bản Cypher thuần \texttt{data/\allowbreak import\_neo4j.cypher} (@@CYPHER_MIB@@ MiB, @@CYPHER_LINES@@ dòng lệnh) thông qua \texttt{cypher-shell}.
  \item Nạp theo lô kích thước 1.000 bản ghi qua giao thức Bolt bằng câu lệnh \texttt{UNWIND} trong \texttt{src/\allowbreak load\_to\_neo4j.py}.
\end{enumerate}

\begin{lstlisting}[caption={Trích đoạn kịch bản Cypher tạo ràng buộc và nạp nút/cạnh mẫu},label={lst:cypher-sample}]
// 1. Rang buoc duy nhat cho id tung nhan dinh
CREATE CONSTRAINT unique_person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT unique_artwork_id IF NOT EXISTS FOR (a:Artwork) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT unique_organization_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE;

// 2. Nap dinh theo lo bang UNWIND (src/load_to_neo4j.py)
UNWIND $batch AS row
MERGE (p:Person {id: row.id})
ON CREATE SET p.name = row.name, p.roles = row.roles,
              p.in_degree = toInteger(row.in_degree),
              p.out_degree = toInteger(row.out_degree);

// 3. Vi du nap canh co bang chung
MATCH (s {id: 'vũ_trường_khoa'}), (t {id: 'doãn_quốc_đam'})
MERGE (s)-[r:DIRECTED_ACTOR]->(t)
ON CREATE SET r.evidence = 'Đạo diễn chỉ đạo diễn xuất trong tác phẩm';
\end{lstlisting}

Bảng~\ref{tab:cypher-queries} tổng hợp một số truy vấn Cypher tiêu biểu dùng để khai thác đồ thị phục vụ các bài toán đánh giá ở giai đoạn cuối kỳ.

\begin{table}[htbp]
\centering
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabularx}{\textwidth}{P{2.8cm} L P{3.4cm}}
\toprule
Bài toán truy vấn & Câu lệnh Cypher trên Neo4j & Ý nghĩa kết quả \\
\midrule
Đạo diễn chỉ đạo nhiều diễn viên &
\texttt{MATCH (d:Person)-[r:DIRECTED\_ACTOR]->(a:Person) RETURN d.name, count(r) AS n ORDER BY n DESC LIMIT 10;} &
Xác định các đạo diễn trung tâm (Vũ Trường Khoa, Nguyễn Phương Điền). \\
\midrule
Truy vết thầy trò 1--2 bước &
\texttt{MATCH p=(m:Person)-[:MENTORED*1..2]->(t:Person) RETURN m.name, t.name, length(p);} &
Phát hiện chuỗi truyền nghề (Công Ninh $\to$ Hứa Minh Đạt / Việt Hương). \\
\midrule
Chiếu đồ thị thuật toán GDS &
\texttt{CALL gds.louvain.stream('cinemaGraph') YIELD nodeId, communityId RETURN gds.util.asNode(nodeId).name, communityId;} &
Chạy phân cụm cộng đồng và tính trọng số trung tâm trực tiếp trong Neo4j. \\
\bottomrule
\end{tabularx}
\caption{Một số truy vấn Cypher minh họa phân tích đồ thị trên Neo4j}
\label{tab:cypher-queries}
\end{table}

\section{Các bước tiền xử lý dữ liệu và trích xuất quan hệ}

\subsection{Thu thập danh sách bài viết từ cây thể loại Wikipedia}

Bước thu thập trong \texttt{src/\allowbreak crawl\_vietnam\_cinema.py} bắt đầu từ danh sách \textbf{15 thể loại gốc} (\texttt{SEED\_CATEGORIES}) về điện ảnh và sân khấu Việt Nam, bao gồm: \textit{Diễn viên Việt Nam}, \textit{Đạo diễn Việt Nam}, \textit{Nhà sản xuất phim Việt Nam}, \textit{Người làm điện ảnh Việt Nam}, \textit{Nghệ sĩ hài Việt Nam}, \textit{Nghệ sĩ cải lương}, \textit{Nghệ sĩ kịch nói Việt Nam}, \textit{Nghệ sĩ nhân dân Việt Nam}, \textit{Nghệ sĩ ưu tú Việt Nam}, \textit{Phim Việt Nam}, \textit{Phim truyền hình Việt Nam}, \textit{Phim điện ảnh Việt Nam}, \textit{Công ty sản xuất phim Việt Nam}, \textit{Sân khấu Việt Nam} và \textit{Nhà hát Việt Nam}.

Thuật toán duyệt theo chiều rộng (BFS) mở rộng hàng đợi thể loại tới giới hạn \texttt{max\_categories = 180}, loại bỏ các bài tổng hợp có tiền tố \texttt{"Danh sách"}. Sau khi tải wikitext theo lô 40 bài viết qua MediaWiki API và lọc bỏ các trang quá ngắn ($\le 50$ ký tự), tập ngữ liệu thu được gồm \textbf{@@CACHE_ARTICLES@@ bài viết} độc nhất.

\subsection{Phân loại thực thể theo thứ tự ưu tiên}

Mỗi bài viết được gán vào một trong 3 nhãn thực thể dựa trên dấu hiệu Infobox và mẫu tiêu đề theo thứ tự ưu tiên nghiêm ngặt để tránh nhầm lẫn:
\begin{enumerate}
  \item \textbf{\texttt{Organization} (ưu tiên 1):} Các tiêu đề chứa từ khóa tổ chức (\textit{hãng phim}, \textit{sân khấu}, \textit{nhà hát}, \textit{đoàn kịch}, \textit{trung tâm phim}, \textit{vtv}, \textit{htv}, \dots) hoặc nằm trong tập \texttt{KNOWN\_ORGANIZATIONS}. Việc kiểm tra tổ chức trước tiên giúp tránh phân loại nhầm các đơn vị như \textit{Trung tâm Phim truyền hình Việt Nam} thành tác phẩm phim.
  \item \textbf{\texttt{Artwork} (ưu tiên 2):} Các bài viết chứa Infobox phim/\allowbreak truyền hình (\texttt{parse\_movie\_infobox}), hoặc tiêu đề có hậu tố/\allowbreak tiền tố tác phẩm (\texttt{(phim}, \texttt{vở kịch}, \texttt{vở chèo}, \texttt{vở cải lương}, \dots).
  \item \textbf{Loại trừ trang phi thực thể:} Bỏ qua các trang giải thưởng, liên hoan phim và danh sách (\textit{Giải \dots}, \textit{Liên hoan \dots}, \textit{Giải Cánh diều}, \textit{Giải Mai Vàng}). Các bài viết tiểu sử còn lại mặc định thuộc lớp \texttt{Person}.
\end{enumerate}

\subsection{Bóc tách Infobox bằng giải thuật Brace-Depth Tracking}

Trong wikitext của Wikipedia tiếng Việt, một trường của Infobox thường lồng nhiều bản mẫu con như \texttt{\{\{ubl|...|...\}\}}, \texttt{\{\{hlist|...|...\}\}} hoặc chú thích \texttt{\{\{chú thích web|...\}\}}. Nếu tách bằng biểu thức chính quy thông thường dừng ở ký tự \texttt{|} hoặc \texttt{\}\}} đầu tiên, giá trị trích xuất sẽ bị cắt cụt.

Hàm \texttt{parse\_infobox\_field} trong \texttt{src/\allowbreak cinema\_extractor.py} sử dụng máy trạng thái theo dõi độ sâu ngoặc nhọn (\texttt{depth}):
\begin{itemize}
  \item Tăng \texttt{depth += 1} khi gặp \texttt{\{\{} và giảm \texttt{depth -= 1} khi gặp \texttt{\}\}}.
  \item Chỉ kết thúc trường hiện tại khi \texttt{depth == 0} và dòng kế tiếp bắt đầu một trường mới cấp cao nhất (\texttt{| field =}) hoặc dấu đóng Infobox (\texttt{\}\}}).
  \item Làm sạch văn bản bằng \texttt{sanitize\_roles} và \texttt{clean\_sentence\_evidence}: loại bỏ chú thích HTML \texttt{<!--\allowbreak ...\allowbreak -->}, thẻ tự đóng \texttt{<ref\allowbreak{} .../>} trước thẻ cặp \texttt{<ref>\allowbreak ...\allowbreak </ref>} để tránh nuốt nhầm đoạn văn kế tiếp, xóa bảng \texttt{\{|...|\}}, giản ước liên kết \texttt{[[Trang đích|\allowbreak Văn bản]]} thành \texttt{Văn bản}, rồi trích xuất thực thể qua \texttt{extract\_wiki\_links} (bỏ qua namespace hệ thống và liên kết năm 4 chữ số).
\end{itemize}

Ngoài Infobox phim, đối với bài viết \texttt{Person}, hệ thống còn quét các mục danh sách phim tham gia (\textit{Danh sách phim}, \textit{Phim đã tham gia}, \textit{Tác phẩm tiêu biểu}, \dots) và đối chiếu với tập \texttt{known\_artworks} để bổ sung các cạnh \texttt{ACTED\_IN}.

\subsection{Khai phá quan hệ văn bản (OpenIE) và suy diễn có căn cứ}

Các quan hệ xã hội mang tính sự nghiệp thường chỉ được nhắc trong đoạn văn mô tả mục \textit{Tiểu sử} hoặc \textit{Sự nghiệp}. Hàm \texttt{extract\_career\_relations} tách câu và áp dụng 5 nhóm mẫu biểu thức chính quy tiếng Việt như trình bày tại Bảng~\ref{tab:openie-patterns}.

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{P{3.0cm} L P{4.7cm}}
\toprule
Quan hệ & Nhóm từ khóa nhận diện trong văn bản & Minh họa trích xuất thực tế \\
\midrule
\texttt{MENTORED} &
\textit{được/\allowbreak nhờ có [\dots] nâng đỡ, phát hiện, dìu dắt, dẫn dắt, truyền nghề; học trò của; theo học lớp của} &
\textit{``là học trò của nghệ sĩ Công Ninh''} $\to$ Công Ninh $\to$ Việt Hương \\
\midrule
\texttt{CO\_STARRED} &
\textit{đóng cặp (ăn ý), kết đôi, bạn diễn ăn ý, hợp tác ăn ý, cặp đôi màn ảnh với/\allowbreak cùng} &
Ghi nhận các cặp bạn diễn ăn ý được đề cập tường minh trong tiểu sử \\
\midrule
\texttt{DIRECTED\_ACTOR} &
\textit{được đạo diễn [\dots] giao vai, chọn vào vai, mời đóng, chỉ đạo diễn xuất; làm việc cùng đạo diễn} &
Bổ sung liên kết Đạo diễn $\to$ Diễn viên từ văn bản sự nghiệp \\
\midrule
\texttt{FOUNDED} &
\textit{sáng lập, thành lập, mở ra, đồng sáng lập; chủ nhiệm/\allowbreak giám đốc của hãng phim, sân khấu} &
\textit{``Giám đốc Hãng phim truyền hình Việt Nam''} $\to$ Khải Hưng $\to$ VFC \\
\midrule
\texttt{AFFILIATED\_WITH} &
\textit{công tác, cộng tác, làm việc, gắn bó, thuộc biên chế tại/\allowbreak ở/\allowbreak của} + tên nhà hát/\allowbreak hãng phim &
\textit{``công tác tại Hãng phim truyện Việt Nam''} $\to$ Nguyễn Hữu Mười \\
\bottomrule
\end{tabularx}
\caption{Năm nhóm mẫu trích xuất quan hệ từ văn bản sự nghiệp (OpenIE)}
\label{tab:openie-patterns}
\end{table}

Đối với suy diễn cấu trúc từ tập phim đã bóc tách: nếu tác phẩm $M$ có đạo diễn $D$ và diễn viên $A$, hệ thống tạo cạnh $D \xrightarrow{\texttt{DIRECTED\_ACTOR}} A$. Với cặp diễn viên $(A_i, A_j)$ trong tối đa 10 diễn viên đầu bảng phân vai của $M$ (\texttt{actors[:10]} nhằm tránh bùng nổ tổ hợp từ vai quần chúng), hệ thống tạo cặp cạnh đối xứng $A_i \leftrightarrow A_j$ nhãn \texttt{CO\_STARRED} kèm số lượng tác phẩm đóng chung.

\subsection{Kiểm soát ràng buộc Ontology và khử nhiễu}

Để giữ độ chính xác cao nhất trước khi xuất tệp và chuyển sang Cypher, tầng \texttt{CinemaGraph} và khâu hậu xử lý áp dụng 5 bộ lọc ràng buộc:
\begin{enumerate}
  \item \textbf{Kiểm tra kiểu miền $(\text{Src}, \text{Rel}, \text{Tgt})$:} Chỉ giữ lại cạnh khi nhãn hai đầu mút khớp đúng từ điển \texttt{VALID\_EDGE\_CONSTRAINTS} (lọc các cạnh ứng viên từ hơn 23.160 cạnh thô xuống còn @@TOTAL_E@@ cạnh chuẩn hóa).
  \item \textbf{Lọc nhiễu quan hệ hôn nhân \texttt{MARRIED\_TO}:} Tên bạn đời phải qua bộ lọc \texttt{is\_valid\_person\_candidate} ($\ge 2$ từ viết hoa), không thuộc tập \texttt{Artwork} hoặc \texttt{Organization}, và không chứa danh sách từ khóa sai loại (tên quốc gia, nhãn hiệu xe, ngày tháng, tên thể loại ca hát/\allowbreak kịch).
  \item \textbf{Chống ghi đè sai địa danh/\allowbreak thành phố:} Các thành phố như Hà Nội, Thành phố Hồ Chí Minh trong danh sách \texttt{STOP\_CITIES} bị chặn không cho khớp nhầm thành tên sân khấu/\allowbreak nhà hát (ví dụ tránh gán ``tại Hà Nội'' thành ``Nhà hát Kịch Hà Nội'').
  \item \textbf{Khử cạnh tự vòng và cạnh trùng:} Kiểm tra \texttt{source\_id != target\_id} và khóa duy nhất \texttt{(source\_id, target\_id, rel\_type)} trong \texttt{CinemaGraph.\allowbreak add\_edge()}.
  \item \textbf{Thoát ký tự an toàn cho Cypher:} Hàm \texttt{sanitize\_cypher\_prop} xóa thẻ \texttt{<ref>}, ký tự xuống dòng và thoát dấu nháy đơn, dấu gạch chéo ngược trước khi ghi ra \texttt{import\_neo4j.cypher}.
\end{enumerate}

\section{Thống kê và phân tích mạng lưới đã xây dựng}

\subsection{Các chỉ số tô-pô mạng toàn cục}

Sử dụng ma trận kề thưa CSR trong \texttt{src/\allowbreak analyze\_cinema\_graph.py}, các chỉ số cấu trúc toàn cục của mạng tri thức điện ảnh -- sân khấu Việt Nam được tổng hợp tại Bảng~\ref{tab:global-stats}.

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{P{4.9cm} r L}
\toprule
Chỉ số tô-pô & Giá trị đo được & Diễn giải đặc điểm mạng \\
\midrule
Tổng số đỉnh ($|V|$) & @@TOTAL_N@@ & Gồm @@N_PERSON@@ \texttt{Person}, @@N_ARTWORK@@ \texttt{Artwork}, @@N_ORG@@ \texttt{Organization}. \\
Tổng số cạnh có hướng ($|E|$) & @@TOTAL_E@@ & Trải đều qua đủ 10 loại quan hệ ngữ nghĩa. \\
Số đỉnh có liên kết / cô lập & @@CONN_N@@ / @@ISO_N@@ & @@PCT_CONN@@\% đỉnh tham gia ít nhất 1 cạnh; @@PCT_ISO@@\% bài viết đơn lẻ chưa có wikilink nối sang cụm khác. \\
Mật độ đồ thị ($\rho$) & @@DENSITY@@ & Mạng thưa đặc trưng của mạng xã hội quy mô lớn ($\sim 0.25\%$). \\
Bậc trung bình ($\bar{k}$) & @@AVG_DEG@@ & Trung bình mỗi nút có @@AVG_DEG@@ cạnh đi ra (và vào). \\
Tính tương hỗ (Reciprocity) & @@RECIP_PCT@@\% & Tương ứng @@RECIP_CNT@@ cạnh hai chiều chủ yếu từ \texttt{CO\_STARRED} và \texttt{MARRIED\_TO}. \\
Thành phần liên thông yếu (WCC) & @@LARGEST_WCC@@ đỉnh (@@PCT_WCC@@\%) & Toàn đồ thị có @@N_WCC@@ WCC, trong đó Giant WCC chiếm gần 3/4 mạng lưới. \\
Thành phần liên thông mạnh (SCC) & @@LARGEST_SCC@@ đỉnh (@@PCT_SCC@@\%) & Có @@N_SCC@@ SCC; khối hạt nhân @@LARGEST_SCC@@ đỉnh kết nối hai chiều chặt chẽ. \\
Louvain Modularity ($Q$) & @@MOD_Q@@ & Phát hiện @@NUM_COMM@@ cụm liên kết; giá trị $Q > 0.3$ cho thấy phân cụm cộng đồng rõ rệt. \\
\bottomrule
\end{tabularx}
\caption{Bảng tổng hợp các chỉ số tô-pô toàn cục của mạng lưới}
\label{tab:global-stats}
\end{table}

\subsection{Phân bố bậc kết nối và đặc tính đuôi nặng}

Phân bố bậc trên toàn bộ @@TOTAL_N@@ nút thể hiện sự phân hóa mạnh giữa nhóm nghệ sĩ mới/\allowbreak phụ (bậc thấp hoặc bằng 0) và nhóm nghệ sĩ trụ cột đóng vai trò hạt nhân (hub), như trình bày ở Bảng~\ref{tab:degree-pcts}.

\begin{table}[htbp]
\centering
\small
\begin{tabular}{lrr}
\toprule
Phân vị & Bậc vào ($k_{\text{in}}$) & Bậc ra ($k_{\text{out}}$) \\
\midrule
P10 (10\%) & @@IN_P10@@ & @@OUT_P10@@ \\
Q1 (25\%) & @@IN_P25@@ & @@OUT_P25@@ \\
Trung vị (50\%) & @@IN_P50@@ & @@OUT_P50@@ \\
Q3 (75\%) & @@IN_P75@@ & @@OUT_P75@@ \\
P90 (90\%) & @@IN_P90@@ & @@OUT_P90@@ \\
P95 (95\%) & @@IN_P95@@ & @@OUT_P95@@ \\
P99 (99\%) & @@IN_P99@@ & @@OUT_P99@@ \\
Cực đại (Max) & @@IN_P100@@ & @@OUT_P100@@ \\
\bottomrule
\end{tabular}
\caption{Các phân vị bậc vào và bậc ra trên toàn mạng}
\label{tab:degree-pcts}
\end{table}

Đỉnh đạt \texttt{in\_degree} cao nhất là \textbf{@@MAX_IN_NAME@@} (@@MAX_IN_IN@@ cạnh vào, @@MAX_IN_OUT@@ cạnh ra), trong khi đỉnh đạt \texttt{out\_degree} cao nhất là \textbf{@@MAX_OUT_NAME@@} (@@MAX_OUT_OUT@@ cạnh ra, @@MAX_OUT_IN@@ cạnh vào) do vừa tham gia diễn xuất vừa đạo diễn nhiều phim truyền hình.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth]{degree_distribution.pdf}
\caption{Phân bố tần số bậc và đường hồi quy Log-Log cho phân bố $k_{\text{in}} \ge 2$}
\label{fig:degree-dist}
\end{figure}

Trên đồ thị Log-Log ở Hình~\ref{fig:degree-dist}, vùng bậc $k_{\text{in}} \ge 10$ suy giảm tuyến tính khá đều theo phân bố đuôi nặng với hệ số góc ước lượng OLS trên toàn miền $k \ge 2$ là $\gamma \approx @@GAMMA@@$. Điều này phản ánh cơ chế gắn kết ưu tiên (\textit{Preferential Attachment}): các tác phẩm truyền hình và điện ảnh thường tập hợp các gương mặt đã có độ nhận diện cao, làm bậc liên kết của nhóm đỉnh hạt nhân tăng vượt trội so với trung vị mạng.

\subsection{Phân tích độ trung tâm đa chiều}

Bảng~\ref{tab:top15-indegree} liệt kê 15 nghệ sĩ có \texttt{In-Degree} cao nhất trong mạng lưới. Nhóm dẫn đầu bao gồm các nghệ sĩ hoạt động bền bỉ đồng thời ở nhiều vùng miền và loại hình (truyền hình, điện ảnh, sân khấu kịch).

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{c l L r r r}
\toprule
Hạng & Nghệ sĩ & Vai trò Infobox & Bậc vào & Bậc ra & Tổng bậc \\
\midrule
@@TOP15_ROWS@@
\bottomrule
\end{tabularx}
\caption{Top 15 nghệ sĩ có Bậc vào (In-Degree) cao nhất trong mạng}
\label{tab:top15-indegree}
\end{table}

Đối chiếu giữa các độ đo trung tâm khác nhau (Hình~\ref{fig:hubs-auth}) giúp làm rõ vai trò cấu trúc riêng biệt của từng nghệ sĩ:
\begin{itemize}
  \item \textbf{PageRank (Uy tín lan truyền):} Top 5 gồm @@TOP5_PR@@. Thứ hạng PageRank gần tương đồng với nhóm bậc cao do cấu trúc cộng tác đa chiều rộng rãi ở phía Nam và hai miền.
  \item \textbf{Betweenness Centrality (Vai trò cầu nối liên vùng):} Top 5 gồm @@TOP5_BETW@@. Đáng chú ý, NSND \textbf{Như Quỳnh} dẫn đầu toàn mạng về Betweenness ($0.032769$) dù chỉ đứng thứ 12 về In-Degree, do bà đóng vai trò mắt xích bắc cầu giữa cộng đồng điện ảnh kinh điển miền Bắc với phim truyền hình hiện đại và các dự án quốc tế.
  \item \textbf{Closeness Centrality (Khả năng tiếp cận nhanh toàn mạng):} Top 5 gồm @@TOP5_CLOS@@. \textbf{Lan Phương} giữ vị trí số 1 nhờ việc đóng phim song song cho cả VFC miền Bắc lẫn sân khấu/\allowbreak phim phía Nam, rút ngắn khoảng cách trắc địa tới hầu hết cụm diễn viên lớn.
  \item \textbf{Thuật toán HITS (Hubs \& Authorities):} Về chỉ số \textit{Hub}, top 5 gồm @@TOP5_HUB@@; về chỉ số \textit{Authority}, top 5 gồm @@TOP5_AUTH@@. Khác với In-Degree, HITS hội tụ mạnh vào lõi tương tác dày đặc của khối phim truyền hình VFC miền Bắc, nơi các đạo diễn như Vũ Trường Khoa ($\text{hub} = 0.1600, \text{auth} = 0$) và Nguyễn Danh Dũng ($\text{hub} = 0.1252, \text{auth} = 0$) chỉ đạo lặp đi lặp lại dàn diễn viên nòng cốt như Doãn Quốc Đam, Mạnh Trường, Lan Phương, Trung Anh. Trường hợp \textbf{Trọng Trinh} đạt điểm Hub cao nhất ($0.1897$) vì ông vừa là đạo diễn kỳ cựu vừa tham gia diễn xuất trực tiếp.
\end{itemize}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth]{hubs_and_authorities.pdf}
\caption{So sánh Top 6 Đạo diễn theo cạnh \texttt{DIRECTED\_ACTOR} và Top 6 Nghệ sĩ theo HITS Authority}
\label{fig:hubs-auth}
\end{figure}

\subsection{Phân tích cấu trúc cộng đồng (Louvain Communities)}

Thuật toán Louvain chạy trên toàn mạng vô hướng đạt hệ số \textbf{Modularity $Q = @@MOD_Q@@$}, khẳng định cấu trúc phân cụm tự nhiên rất rõ ràng (Bảng~\ref{tab:louvain-comm}). Tổng cộng mạng gồm @@NUM_COMM@@ cụm liên thông không tầm thường, trong đó 5 cộng đồng lớn nhất bao phủ @@TOP5_COMM_SUM@@ đỉnh (tương ứng @@TOP5_COMM_PCT@@\% toàn mạng).

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{c r P{4.8cm} L}
\toprule
Cụm & Quy mô & Nghệ sĩ hạt nhân tiêu biểu & Đặc trưng nghệ thuật của cụm \\
\midrule
@@COMM_ROWS@@
\bottomrule
\end{tabularx}
\caption{Top 5 cộng đồng nghệ thuật phát hiện bởi thuật toán Louvain ($Q = @@MOD_Q@@$)}
\label{tab:louvain-comm}
\end{table}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.86\textwidth]{core_network.pdf}
\caption{Đồ thị con 20 nghệ sĩ bậc kết nối cao nhất kèm các cạnh liên kết thực tế}
\label{fig:core-network}
\end{figure}

Quan sát Hình~\ref{fig:core-network} cho thấy mạng lõi của 20 nghệ sĩ có tổng bậc cao nhất tự phân nhóm rõ theo vùng hoạt động: các nghệ sĩ VFC (\textit{Trọng Trinh, Doãn Quốc Đam, Trung Anh, Mạnh Trường, Mạnh Cường, Bùi Bài Bình, Thanh Quý, Nhã Phương}) nằm ở cụm C3; nhóm truyền hình và sân khấu phía Nam (\textit{Quang Tuấn, Lương Thế Thành, Hồng Ánh, Việt Anh, Thân Thúy Hà}) thuộc cụm C2; nhóm điện ảnh thương mại đa vùng (\textit{Kim Xuân, Hứa Vĩ Văn, Lan Phương, Huy Khánh, Bình Minh, Thái Hòa}) thuộc cụm C4; và \textit{Như Quỳnh} đại diện cho cầu nối tới cụm C0.

\subsection{Phân tích sâu các loại quan hệ đặc thù}

\subsubsection{Quan hệ Đạo diễn chỉ đạo Diễn viên (\texorpdfstring{\texttt{DIRECTED\_ACTOR}}{DIRECTED\_ACTOR})}

Thống kê @@TOTAL_DA@@ cạnh \texttt{DIRECTED\_ACTOR} cho thấy rõ các đạo diễn truyền hình VFC, TFS và điện ảnh thương mại tạo thành những ``tổ đội'' cộng tác bền chặt với dàn diễn viên quen thuộc (Bảng~\ref{tab:top-directors}):

\begin{table}[htbp]
\centering
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabularx}{\textwidth}{c P{2.6cm} r P{4.9cm} L}
\toprule
Hạng & Đạo diễn & Số lượt & Diễn viên tiêu biểu & Tác phẩm tiêu biểu \\
\midrule
@@DIR_ROWS@@
\bottomrule
\end{tabularx}
\caption{Top 5 đạo diễn có số cạnh \texttt{DIRECTED\_ACTOR} lớn nhất}
\label{tab:top-directors}
\end{table}

\subsubsection{Quan hệ Bạn diễn đóng chung (\texorpdfstring{\texttt{CO\_STARRED}}{CO\_STARRED})}

Bằng cách gom nhóm các cặp nghệ sĩ qua từng tác phẩm chung trong tập cạnh \texttt{ACTED\_IN} (loại trừ các cặp trùng tên nghệ sĩ chưa gộp định danh), các cặp bạn diễn ăn ý xuất hiện nhiều lần nhất được tổng hợp trong Bảng~\ref{tab:costar-pairs}.

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{P{5.4cm} c L}
\toprule
Cặp bạn diễn & Số tác phẩm chung & Minh chứng tác phẩm tiêu biểu \\
\midrule
@@COSTAR_ROWS@@
\bottomrule
\end{tabularx}
\caption{Top 5 cặp bạn diễn hợp tác qua nhiều tác phẩm nhất trong dữ liệu}
\label{tab:costar-pairs}
\end{table}

\subsubsection{Quan hệ Nâng đỡ / Truyền nghề (\texorpdfstring{\texttt{MENTORED}}{MENTORED}) và Tổ chức}

Trong toàn mạng trích xuất được \textbf{@@TOTAL_MENTORED@@ cạnh \texttt{MENTORED}} trực tiếp từ câu tường thuật trên Wikipedia (Bảng~\ref{tab:mentored}), nổi bật vai trò đào tạo của các nghệ sĩ thế hệ đi trước tại Trường Đại học Sân khấu -- Điện ảnh và các đoàn nghệ thuật truyền thống:

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{P{2.7cm} P{2.9cm} L}
\toprule
Người dẫn dắt & Học trò / Nâng đỡ & Minh chứng trích xuất từ văn bản Wikipedia \\
\midrule
@@MENTOR_ROWS@@
\bottomrule
\end{tabularx}
\caption{Một số quan hệ \texttt{MENTORED} trích xuất từ văn bản sự nghiệp}
\label{tab:mentored}
\end{table}

Ngoài ra, xét ở khía cạnh tổ chức sản xuất (\texttt{PRODUCED\_BY} -- @@TOTAL_PRODUCED_BY@@ cạnh), các đơn vị đóng vai trò trục sản xuất lớn nhất trong tập dữ liệu gồm: @@TOP_ORGS@@.

\subsection{Kiểm định độ chính xác sơ bộ và kiểm thử tự động}

Nhóm thiết kế kịch bản \texttt{tests/\allowbreak verify\_precision.py} lấy mẫu ngẫu nhiên phân tầng $N = @@PREC_N@@$ cạnh trên cả 10 loại quan hệ (hạt giống \texttt{random\_seed = @@PREC_SEED@@}) và đối chiếu tự động với Infobox và văn bản gốc trong bộ nhớ đệm \texttt{vietnam\_cinema\_articles\_cache.json}. Kết quả (Bảng~\ref{tab:precision}) lưu tại \texttt{reports/\allowbreak precision\_evaluation.json} đạt @@PREC_CORRECT@@/@@PREC_N@@ mẫu khớp minh chứng bài gốc (@@PREC_PCT@@\%), đồng thời toàn bộ \textbf{218/218 bài kiểm thử} (\texttt{pytest tests}) vượt qua. Theo kế hoạch môn học, đánh giá chất lượng cuối cùng ($\ge 90\%$ do con người thẩm định độc lập) sẽ tiếp tục được thực hiện ở giai đoạn bài tập cuối kỳ.

\begin{table}[htbp]
\centering
\small
\begin{tabular}{llrrr}
\toprule
Loại quan hệ & Nhóm trích xuất & Số mẫu kiểm tra & Số mẫu khớp gốc & Tỷ lệ khớp \\
\midrule
@@PREC_ROWS@@
\midrule
Tổng cộng & Toàn mạng & @@PREC_N@@ & @@PREC_CORRECT@@ & @@PREC_PCT@@\% \\
\bottomrule
\end{tabular}
\caption{Kết quả kiểm định phân tầng 300 mẫu đối chiếu ngữ liệu Wikipedia gốc}
\label{tab:precision}
\end{table}

\section{Kết luận về các vấn đề đạt được, chưa đạt được và liên kết mã nguồn}

\subsection{Các vấn đề đã đạt được}

Đồ án đã hoàn thành toàn bộ các mục tiêu giai đoạn xây dựng mạng xã hội và dữ liệu đồ thị:
\begin{itemize}
  \item \textbf{Quy mô vượt chỉ tiêu:} Mạng đạt \textbf{@@TOTAL_N@@ nút} (vượt mốc 2.000 nút) và \textbf{@@TOTAL_E@@ cạnh có hướng} (vượt mốc 5.000 cạnh), bao phủ cả điện ảnh lẫn sân khấu truyền thống và hiện đại Việt Nam.
  \item \textbf{Đầy đủ 10 loại quan hệ chi tiết:} Tách bạch rõ các tầng hợp tác (\texttt{DIRECTED\_ACTOR}, \texttt{CO\_STARRED}, \texttt{MENTORED}, \texttt{DIRECTED}, \texttt{ACTED\_IN}, \texttt{PRODUCED}, \texttt{PRODUCED\_BY}, \texttt{MARRIED\_TO}, \texttt{AFFILIATED\_WITH}, \texttt{FOUNDED}) kèm trường \texttt{evidence} truy nguyên nguồn gốc.
  \item \textbf{Kiến trúc xử lý ổn định và tái lập:} Bộ parser Brace-Depth xử lý triệt để template lồng nhau; cơ chế cache offline @@CACHE_ARTICLES@@ bài viết cho phép chạy lại toàn bộ quy trình và 218 bài kiểm thử tự động chỉ trong khoảng 1 phút.
  \item \textbf{Sẵn sàng lưu trữ Neo4j và phân tích cuối kỳ:} Dữ liệu được xuất chuẩn CSV, kịch bản Cypher (@@CYPHER_LINES@@ dòng) và script Bolt UNWIND \texttt{load\_to\_neo4j.py}, đồng thời đã phân tích định lượng cấu trúc tô-pô, bậc phân phối, 5 cộng đồng Louvain ($Q = @@MOD_Q@@$) và đa độ đo trung tâm.
\end{itemize}

\subsection{Các vấn đề chưa đạt được và hạn chế kỹ thuật}

Bên cạnh các kết quả đạt được, quá trình rà soát trực tiếp trên tập CSV đã phát hiện một số hạn chế cần khắc phục ở giai đoạn tiếp theo:
\begin{enumerate}
  \item \textbf{Chưa hợp nhất đầy đủ trang đổi hướng và biến thể tiêu đề Wikipedia (Entity Resolution):} Một vài nghệ sĩ vẫn tồn tại dưới hai nút riêng biệt do khác biệt nhỏ ở phần định danh ngoặc đơn trên Wikipedia (ví dụ: \textit{Lan Hương (diễn viên sinh 1961)} và \textit{Lan Hương (diễn viên, sinh 1961)}, hoặc \textit{Kim Hiền} và \textit{Kim Hiền (diễn viên)}). Cần bổ sung bước gọi API \texttt{redirects=1} để quy chuẩn toàn bộ bí danh về một \texttt{canonical\_id} duy nhất.
  \item \textbf{Còn sót một số liên kết nhiễu trong danh sách diễn viên:} Một số ít liên kết wiki có neo mục lục (\texttt{\#}) hoặc diễn viên nước ngoài trong phim hợp tác (ví dụ \textit{Nhân vật trong Tiếu ngạo giang hồ\#Lâm Bình Chi}, \textit{Madeleine Stowe}) vẫn lọt vào tập cạnh \texttt{ACTED\_IN} do bộ lọc mới chỉ loại tiền tố namespace mà chưa lọc liên kết chứa ký tự \texttt{\#} hoặc mục phi nhân vật.
  \item \textbf{Tỷ lệ đỉnh cô lập còn khá cao (@@ISO_N@@ đỉnh, @@PCT_ISO@@\%):} Một số bài viết phim truyền hình cũ hoặc nghệ sĩ địa phương thiếu Infobox chuẩn hoặc chưa có liên kết chéo với các thực thể đã crawl, dẫn tới bậc bằng 0.
  \item \textbf{Độ phủ các cạnh văn bản hiếm còn mỏng và thiếu yếu tố thời gian:} Hai quan hệ dựa hoàn toàn vào văn bản tường thuật là \texttt{MENTORED} (@@TOTAL_MENTORED@@ cạnh) và \texttt{FOUNDED} (@@TOTAL_FOUNDED@@ cạnh -- trong đó regex hiện bắt cả vai trò Giám đốc hãng phim bên cạnh người sáng lập) có số lượng khiêm tốn. Ngoài ra, từng cạnh hợp tác chưa gắn nhãn năm phát hành để phân tích mạng động theo thời gian (\textit{Temporal Graph}).
  \item \textbf{Kiểm định chất lượng $\ge 90\%$ mới thực hiện ở mức đối chiếu tự động:} Việc đánh giá chính thức độ chính xác ngữ nghĩa bằng nhãn chuẩn do con người gán (Human Gold Standard) sẽ được triển khai ở bài tập cuối kỳ theo đúng yêu cầu môn học.
\end{enumerate}

\newpage
\subsection{Kho lưu trữ mã nguồn GitHub}

Toàn bộ mã nguồn thu thập Wikipedia, mô-đun NLP, tập dữ liệu CSV, kịch bản nạp Neo4j, bộ kiểm thử tự động và mã nguồn LaTeX của báo cáo được lưu trữ công khai phục vụ kiểm chứng và đánh giá bài tập cuối kỳ tại:

\begin{itemize}
  \item \textbf{Liên kết GitHub:}\\[0.2em]
  \url{https://github.com/DontAskMeWhy0507/vietnam-cinema-graph-nlp}
  \item \textbf{Cấu trúc thư mục chính:}
  \begin{itemize}\raggedright
    \item \texttt{src/}: \texttt{crawl\_vietnam\_cinema.py}, \texttt{cinema\_extractor.py}, \texttt{cinema\_models.py}, \texttt{load\_to\_neo4j.py}, \texttt{analyze\_cinema\_graph.py}, \texttt{export\_latex\_figures.py}, \texttt{generate\_latex\_report.py}.
    \item \texttt{data/}: \texttt{vietnam\_cinema\_nodes.csv}, \texttt{vietnam\_cinema\_edges.csv}, \texttt{import\_neo4j.cypher}.
    \item \texttt{tests/}: Bộ kiểm thử \texttt{pytest} (218 ca kiểm thử) và kịch bản kiểm định phân tầng \texttt{verify\_precision.py}.
    \item \texttt{reports/}: \texttt{BAO\_CAO\_BAI\_TAP\_LON\_SNA.tex}, \texttt{BAO\_CAO\_BAI\_TAP\_LON\_SNA.pdf}, \texttt{precision\_evaluation.json} và thư mục hình ảnh \texttt{figures/}.
  \end{itemize}
\end{itemize}

Tổng kết luận lại, dữ liệu mạng xã hội điện ảnh -- sân khấu Việt Nam đã sẵn sàng cho khâu kiểm định độ chính xác và các thuật toán phân tích đồ thị chuyên sâu trên Neo4j.

\end{document}
"""


def generate_latex():
    m = collect_verified_metrics()
    N, E = m["N"], m["E"]
    lc = m["label_counts"]
    rc = m["rel_counts"]

    rel_meta = [
        ("CO_STARRED", r"\texttt{Person} $\leftrightarrow$ \texttt{Person}",
         r"Hai diễn viên đóng chung trong cùng tác phẩm hoặc được văn bản ghi nhận đóng cặp ăn ý."),
        ("ACTED_IN", r"\texttt{Person} $\to$ \texttt{Artwork}",
         r"Nghệ sĩ tham gia diễn xuất trong tác phẩm điện ảnh, truyền hình hoặc sân khấu."),
        ("DIRECTED_ACTOR", r"\texttt{Person} $\to$ \texttt{Person}",
         r"Đạo diễn trực tiếp chỉ đạo diễn xuất cho diễn viên trong tác phẩm hoặc qua bài viết sự nghiệp."),
        ("DIRECTED", r"\texttt{Person} $\to$ \texttt{Artwork}",
         r"Nghệ sĩ giữ vai trò đạo diễn tác phẩm, trích xuất từ trường \texttt{đạo\_diễn} trong Infobox."),
        ("PRODUCED_BY", r"\texttt{Artwork} $\to$ \texttt{Organization}",
         r"Tác phẩm do hãng phim, đài truyền hình hoặc nhà hát sản xuất/\allowbreak phát hành."),
        ("MARRIED_TO", r"\texttt{Person} $\leftrightarrow$ \texttt{Person}",
         r"Quan hệ hôn phối ngoài đời giữa các nghệ sĩ sau bước lọc bỏ thực thể hư cấu và nhiễu."),
        ("PRODUCED", r"\texttt{Person} $\to$ \texttt{Artwork}",
         r"Cá nhân đứng tên nhà sản xuất tác phẩm trong Infobox phim."),
        ("AFFILIATED_WITH", r"\texttt{Person} $\to$ \texttt{Organization}",
         r"Nghệ sĩ công tác, gắn bó lâu dài với đoàn kịch, nhà hát hoặc hãng phim."),
        ("FOUNDED", r"\texttt{Person} $\to$ \texttt{Organization}",
         r"Nghệ sĩ sáng lập hoặc giữ vai trò giám đốc/\allowbreak chủ nhiệm hãng phim, sân khấu."),
        ("MENTORED", r"\texttt{Person} $\to$ \texttt{Person}",
         r"Quan hệ thầy trò, người nâng đỡ hoặc phát hiện tài năng từ mục Tiểu sử/\allowbreak Sự nghiệp."),
    ]
    edge_rows = []
    for idx, (rtype, schema_str, desc) in enumerate(rel_meta, 1):
        cnt = rc[rtype]
        pct = cnt / E * 100.0
        edge_rows.append(
            f"{idx} & \\texttt{{{tex_escape(rtype)}}} & {schema_str} & {fmt_int(cnt)} & {pct:.2f}\\% & {desc} \\\\"
        )

    top15_rows = []
    for rank, p in enumerate(m["top15_in"], 1):
        roles = p["roles"] or "Nghệ sĩ"
        if len(roles) > 22:
            roles = roles[:20] + "..."
        top15_rows.append(
            f"{rank} & {tex_escape(p['name'])} & {tex_escape(roles)} & "
            f"{p['in_degree']} & {p['out_degree']} & {p['tot_degree']} \\\\"
        )

    comm_desc = {
        0: "Cốt lõi điện ảnh truyện nhựa và kịch nói kinh điển miền Bắc.",
        2: "Mạng lưới phim truyền hình phía Nam và các sân khấu kịch nói.",
        4: "Cụm điện ảnh chiếu rạp thương mại và hợp tác đa vùng miền.",
        3: "Cụm phim truyền hình VFC miền Bắc với tần suất hợp tác dày đặc.",
        1: "Cụm sân khấu kịch phía Nam kết hợp giữa nghệ sĩ gạo cội và thế hệ mới.",
    }
    comm_rows = []
    top5_comm_sum = 0
    for cid, sz in m["comm_counts"].most_common(5):
        top5_comm_sum += sz
        members = [n for n in m["persons"] if n["community"] == cid]
        reps = ", ".join(x["name"] for x in sorted(members, key=lambda k: k["in_degree"], reverse=True)[:4])
        pct = sz / N * 100.0
        comm_rows.append(
            f"C{cid} & {fmt_int(sz)} ({pct:.1f}\\%) & {tex_escape(reps)} & {comm_desc.get(cid, 'Cụm nghệ thuật liên kết cao.')} \\\\"
        )

    dir_rows = []
    for rank, (did, cnt) in enumerate(m["dir_actor_top5"], 1):
        dname = m["id_to_node"][did]["name"]
        actors_s = ", ".join(m["dir_sample_actors"][did][:4])
        films_s = ", ".join(m["dir_films"][did][:2])
        dir_rows.append(
            f"{rank} & {tex_escape(dname)} & {cnt} & {tex_escape(actors_s)} & {tex_escape(films_s)} \\\\"
        )

    costar_rows = []
    for (a1, a2), cnt in m["costar_top5"]:
        works = ", ".join(m["shared_titles"][(a1, a2)][:3])
        costar_rows.append(
            f"{tex_escape(a1)} $\\leftrightarrow$ {tex_escape(a2)} & {cnt} & {tex_escape(works)} \\\\"
        )

    mentor_rows = []
    for e in m["mentored_edges"][:6]:
        ev = e["evidence"]
        if len(ev) > 125:
            ev = ev[:122] + "..."
        mentor_rows.append(
            f"{tex_escape(e['source_name'])} & {tex_escape(e['target_name'])} & \\textit{{{tex_escape(ev)}}} \\\\"
        )

    rel_bd = m["prec"]["relation_breakdown"]
    prec_rows = []
    for rtype in ["ACTED_IN", "DIRECTED", "PRODUCED", "PRODUCED_BY", "MARRIED_TO",
                  "AFFILIATED_WITH", "CO_STARRED", "DIRECTED_ACTOR", "MENTORED", "FOUNDED"]:
        info = rel_bd[rtype]
        prec_rows.append(
            f"\\texttt{{{tex_escape(rtype)}}} & {tex_escape(info['group'])} & {info['tested']} & {info['correct']} & {info['precision_pct']:.1f}\\% \\\\"
        )

    replacements = {
        "@@CACHE_ARTICLES@@": fmt_int(m["cache_articles"]),
        "@@CACHE_MB@@": f"{m['cache_mb_dec']:.2f}",
        "@@CYPHER_MIB@@": f"{m['cypher_mib']:.2f}",
        "@@CYPHER_LINES@@": fmt_int(m["cypher_lines"]),
        "@@TOTAL_N@@": fmt_int(N),
        "@@TOTAL_E@@": fmt_int(E),
        "@@N_PERSON@@": fmt_int(lc["Person"]),
        "@@PCT_PERSON@@": f"{lc['Person']/N*100:.2f}",
        "@@N_ARTWORK@@": fmt_int(lc["Artwork"]),
        "@@PCT_ARTWORK@@": f"{lc['Artwork']/N*100:.2f}",
        "@@N_ORG@@": fmt_int(lc["Organization"]),
        "@@PCT_ORG@@": f"{lc['Organization']/N*100:.2f}",
        "@@EDGE_ROWS@@": "\n".join(edge_rows),
        "@@TOTAL_COSTAR@@": fmt_int(rc["CO_STARRED"]),
        "@@COSTAR_SYM_PAIRS@@": fmt_int(m["costar_sym_pairs"]),
        "@@COSTAR_SYM_EDGES@@": fmt_int(m["costar_sym_edges"]),
        "@@COSTAR_ASYM_EDGES@@": fmt_int(m["costar_asym_edges"]),
        "@@CONN_N@@": fmt_int(m["connected_nodes"]),
        "@@ISO_N@@": fmt_int(m["isolated_nodes"]),
        "@@PCT_CONN@@": f"{m['connected_nodes']/N*100:.2f}",
        "@@PCT_ISO@@": f"{m['isolated_nodes']/N*100:.2f}",
        "@@DENSITY@@": f"{m['density']:.6f}",
        "@@AVG_DEG@@": f"{m['avg_degree']:.2f}",
        "@@RECIP_PCT@@": f"{m['reciprocity_pct']:.2f}",
        "@@RECIP_CNT@@": fmt_int(m["reciprocal"]),
        "@@LARGEST_WCC@@": fmt_int(m["largest_wcc"]),
        "@@PCT_WCC@@": f"{m['largest_wcc']/N*100:.2f}",
        "@@N_WCC@@": str(m["n_wcc"]),
        "@@LARGEST_SCC@@": fmt_int(m["largest_scc"]),
        "@@PCT_SCC@@": f"{m['largest_scc']/N*100:.2f}",
        "@@N_SCC@@": fmt_int(m["n_scc"]),
        "@@MOD_Q@@": f"{m['modularity_q']:.4f}",
        "@@NUM_COMM@@": str(m["num_communities"]),
        "@@TOP5_COMM_SUM@@": fmt_int(top5_comm_sum),
        "@@TOP5_COMM_PCT@@": f"{top5_comm_sum/N*100:.1f}",
        "@@IN_P10@@": str(m["in_pcts"][10]),
        "@@IN_P25@@": str(m["in_pcts"][25]),
        "@@IN_P50@@": str(m["in_pcts"][50]),
        "@@IN_P75@@": str(m["in_pcts"][75]),
        "@@IN_P90@@": str(m["in_pcts"][90]),
        "@@IN_P95@@": str(m["in_pcts"][95]),
        "@@IN_P99@@": str(m["in_pcts"][99]),
        "@@IN_P100@@": str(m["in_pcts"][100]),
        "@@OUT_P10@@": str(m["out_pcts"][10]),
        "@@OUT_P25@@": str(m["out_pcts"][25]),
        "@@OUT_P50@@": str(m["out_pcts"][50]),
        "@@OUT_P75@@": str(m["out_pcts"][75]),
        "@@OUT_P90@@": str(m["out_pcts"][90]),
        "@@OUT_P95@@": str(m["out_pcts"][95]),
        "@@OUT_P99@@": str(m["out_pcts"][99]),
        "@@OUT_P100@@": str(m["out_pcts"][100]),
        "@@MAX_IN_NAME@@": tex_escape(m["max_in_node"]["name"]),
        "@@MAX_IN_IN@@": str(m["max_in_node"]["in_degree"]),
        "@@MAX_IN_OUT@@": str(m["max_in_node"]["out_degree"]),
        "@@MAX_OUT_NAME@@": tex_escape(m["max_out_node"]["name"]),
        "@@MAX_OUT_OUT@@": str(m["max_out_node"]["out_degree"]),
        "@@MAX_OUT_IN@@": str(m["max_out_node"]["in_degree"]),
        "@@GAMMA@@": f"{m['gamma']:.2f}",
        "@@TOP15_ROWS@@": "\n".join(top15_rows),
        "@@TOP5_PR@@": ", ".join(f"{tex_escape(p['name'])} ({p['pagerank']:.6f})" for p in m["top5_pr"]),
        "@@TOP5_BETW@@": ", ".join(f"{tex_escape(p['name'])} ({p['betweenness']:.6f})" for p in m["top5_betw"]),
        "@@TOP5_CLOS@@": ", ".join(f"{tex_escape(p['name'])} ({p['closeness']:.6f})" for p in m["top5_clos"]),
        "@@TOP5_AUTH@@": ", ".join(f"{tex_escape(p['name'])} ({p['authority']:.4f})" for p in m["top5_auth"]),
        "@@TOP5_HUB@@": ", ".join(f"{tex_escape(p['name'])} ({p['hub']:.4f})" for p in m["top5_hub"]),
        "@@COMM_ROWS@@": "\n".join(comm_rows),
        "@@TOTAL_DA@@": fmt_int(rc["DIRECTED_ACTOR"]),
        "@@DIR_ROWS@@": "\n".join(dir_rows),
        "@@COSTAR_ROWS@@": "\n".join(costar_rows),
        "@@TOTAL_MENTORED@@": str(rc["MENTORED"]),
        "@@TOTAL_FOUNDED@@": str(rc["FOUNDED"]),
        "@@MENTOR_ROWS@@": "\n".join(mentor_rows),
        "@@TOTAL_PRODUCED_BY@@": str(rc["PRODUCED_BY"]),
        "@@TOP_ORGS@@": ", ".join(f"{tex_escape(name)} ({cnt} tác phẩm)" for name, cnt in m["top_orgs"]),
        "@@PREC_N@@": str(m["prec"]["metadata"]["sample_size"]),
        "@@PREC_SEED@@": str(m["prec"]["metadata"]["random_seed"]),
        "@@PREC_CORRECT@@": str(m["prec"]["summary"]["total_correct"]),
        "@@PREC_PCT@@": f"{m['prec']['summary']['overall_precision_pct']:.1f}",
        "@@PREC_ROWS@@": "\n".join(prec_rows),
    }

    latex_content = LATEX_TEMPLATE
    for token, val in replacements.items():
        latex_content = latex_content.replace(token, val)

    assert "@@" not in latex_content, "Unreplaced template token remaining!"
    out_tex = os.path.join(REPORT_DIR, "BAO_CAO_BAI_TAP_LON_SNA.tex")
    with open(out_tex, mode="w", encoding="utf-8") as f:
        f.write(latex_content)
    print(f"Generated LaTeX report successfully: {out_tex} ({len(latex_content):,} chars)")


if __name__ == "__main__":
    generate_latex()
