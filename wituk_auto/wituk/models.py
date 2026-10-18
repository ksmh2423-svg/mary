from dataclasses import dataclass, field


@dataclass
class Option:
    name: str            # 예: "색상:블랙/사이즈:L"
    extra_price: int = 0  # 기본가 대비 추가금
    stock: int = 0


@dataclass
class Product:
    source: str                  # 소싱처 이름 (domeggook, excel 등)
    source_id: str               # 소싱처 상품번호
    title: str                   # 원본 상품명
    cost: int                    # 도매가(원)
    stock: int = 0
    category: str = ""
    brand: str = ""
    images: list = field(default_factory=list)       # 이미지 URL 또는 파일 경로
    detail_html: str = ""
    options: list = field(default_factory=list)      # [Option]
    source_shipping: int = 0     # 도매처 배송비
    url: str = ""
    currency: str = "KRW"        # 해외 소싱이면 CNY, USD 등

    # 가공 결과 (pipeline에서 채움)
    clean_title: str = ""
    keywords: list = field(default_factory=list)
    sale_price: int = 0
    local_images: list = field(default_factory=list)
    flags: list = field(default_factory=list)        # 금지어·상표·인증 경고
    blocked: bool = False
