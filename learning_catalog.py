"""Offline bilingual navigation catalog, not a duplicate simulation engine.

IDs are stable persistence and routing contracts, independent of UI text.
All chapter coverage is partial; empty routes never imply implementation.
"""
from dataclasses import dataclass
import unicodedata


@dataclass(frozen=True)
class Chapter:
    number:int
    title:tuple
    gap:tuple


CHAPTERS=(
    Chapter(1,("Digital logic","منطق دیجیتال"),("Karnaugh maps and state synthesis remain open.","نقشه کارنو و طراحی ماشین حالت باقی مانده‌اند.")),
    Chapter(2,("Digital components","اجزای دیجیتال"),("More device variants and physical IC pinouts remain open.","گونه‌های بیشتر قطعات و پایه‌های آی‌سی واقعی باقی مانده‌اند.")),
    Chapter(3,("Data representation","نمایش داده"),("Historical floating-point formats and additional coding exercises remain.","قالب‌های تاریخی ممیز شناور و تمرین‌های کدگذاری بیشتر باقی مانده‌اند.")),
    Chapter(4,("Register transfer and microoperations","انتقال ثبات و ریزعملیات"),("Electrical timing and full arithmetic-logic-shift hardware remain.","زمان‌بندی الکتریکی و مدار کامل حسابی‌ـ‌منطقی‌ـ‌شیفت باقی مانده‌اند.")),
    Chapter(5,("Basic Computer design","طراحی کامپیوتر پایه"),("Combined control bits and gate-level implementation remain.","بیت‌های کنترل ترکیبی و پیاده‌سازی سطح گیت باقی مانده‌اند.")),
    Chapter(6,("Programming the Basic Computer","برنامه‌نویسی کامپیوتر پایه"),("More worked subroutine and I/O exercises remain.","تمرین‌های بیشتر زیرروال و ورودی‌ـ‌خروجی باقی مانده‌اند.")),
    Chapter(7,("Microprogrammed control","کنترل ریزبرنامه‌ای"),("Additional instruction mapping and control-store examples remain.","نگاشت دستورها و مثال‌های بیشتر حافظه کنترل باقی مانده‌اند.")),
    Chapter(8,("CPU organization","سازمان پردازنده"),("Full RISC/CISC comparison and instruction encodings remain.","مقایسه کامل RISC/CISC و کدگذاری دستورها باقی مانده‌اند.")),
    Chapter(9,("Pipeline and vector processing","خط لوله و پردازش برداری"),("Variable latency and additional array processor models remain.","تأخیر متغیر و مدل‌های بیشتر پردازنده آرایه‌ای باقی مانده‌اند.")),
    Chapter(10,("Computer arithmetic","محاسبات کامپیوتری"),("Historical floating formats and more algorithms remain.","قالب‌های تاریخی ممیز شناور و الگوریتم‌های بیشتر باقی مانده‌اند.")),
    Chapter(11,("I/O organization","سازمان ورودی و خروجی"),("Serial framing and further I/O integration remain.","قالب‌بندی سریال و یکپارچگی بیشتر ورودی‌ـ‌خروجی باقی مانده‌اند.")),
    Chapter(12,("Memory organization","سازمان حافظه"),("Cache, associative and virtual memory remain.","حافظه نهان، انجمنی و مجازی باقی مانده‌اند.")),
    Chapter(13,("Multiprocessors","چندپردازنده‌ها"),("Crossbar, multistage networks, synchronization and coherence remain.","اتصال متقاطع، شبکه چندمرحله‌ای، همگام‌سازی و انسجام باقی مانده‌اند.")),
)


@dataclass(frozen=True)
class Tool:
    id:str
    chapter:int
    lab:str
    route:str
    title:tuple
    task:tuple
    keywords:str=""


TOOLS=(
    Tool("gates",1,"logic","gates",("Logic gates & truth tables","گیت‌ها و جدول درستی"),("Change circuit inputs and compare Boolean equations with output.","ورودی مدار را تغییر دهید و خروجی را با معادله بولی مقایسه کنید."),"AND OR XOR NAND NOR NOT K-map"),
    Tool("sequential",1,"logic","sequential",("Flip-flops & sequential logic","فلیپ‌فلاپ و منطق ترتیبی"),("Apply a clock edge and compare present and next state.","لبه ساعت اعمال کنید و حالت فعلی و بعدی را مقایسه کنید."),"D JK T SR clock waveform"),
    Tool("components",2,"logic","gates",("Digital component library","کتابخانه قطعات دیجیتال"),("Choose an adder, decoder, encoder or multiplexer and inspect its pins.","جمع‌کننده، دیکدر، انکدر یا مالتی‌پلکسر را انتخاب و پایه‌ها را بررسی کنید."),"MUX DEMUX adder decoder encoder"),
    Tool("registers-counter",2,"logic","sequential",("Registers & counters","ثبات‌ها و شمارنده‌ها"),("Compare shift registers, counters and their state transitions.","ثبات‌های شیفت و شمارنده‌ها و تغییر حالتشان را مقایسه کنید."),"ring Johnson counter shift"),
    Tool("bases",3,"computer","alu",("Number bases & signed words","مبناهای عددی و کلمات علامت‌دار"),("Compare binary, octal, decimal and hexadecimal words.","نمایش دودویی، هشت‌هشتی، ده‌دهی و هگز را مقایسه کنید."),"BIN OCT DEC HEX two complement"),
    Tool("codes",3,"computer","codes",("Data codes","کدهای داده"),("Explore BCD, Gray, ASCII and Hamming code conversions.","تبدیل‌های BCD، گری، ASCII و همینگ را بررسی کنید."),"BCD Gray ASCII Hamming parity"),
    Tool("translator",4,"workspace","translate",("RTL → Assembly translator","مترجم RTL به اسمبلی"),("Choose RTL → ASM, write or build RTL, translate, and export valid assembly.","جهت RTL → ASM را انتخاب کنید، RTL بنویسید یا بسازید، ترجمه و اسمبلی معتبر ذخیره کنید."),"RTL ASM assignment تکلیف"),
    Tool("alu",4,"computer","alu",("Arithmetic logic unit","واحد حساب و منطق"),("Change operands and inspect result, carry and arithmetic stages.","عملوندها را تغییر دهید و نتیجه، نقلی و مراحل محاسباتی را بررسی کنید."),"ALU carry ripple shift"),
    Tool("bus",4,"logic","bus",("Register bus","گذرگاه ثبات‌ها"),("Select drivers and inspect tri-state and conflicting outputs.","راه‌اندازها را انتخاب و خروجی سه‌حالته و تداخل را بررسی کنید."),"bus Z X tristate"),
    Tool("basic-cpu",5,"computer","live",("Basic Computer datapath","مسیر داده کامپیوتر پایه"),("Execute an instruction and inspect real register transfers.","یک دستور اجرا کنید و انتقال واقعی ثبات‌ها را ببینید."),"CPU AC DR AR PC IR"),
    Tool("cpu-state",5,"computer","register-memory",("CPU registers & memory","ثبات‌ها و حافظه CPU"),("Step instructions and examine the stored words.","دستورها را گام‌به‌گام اجرا و کلمات ذخیره‌شده را بررسی کنید."),"register memory"),
    Tool("cycles",5,"computer","cycles",("Instruction timing & control","زمان‌بندی و کنترل دستور"),("Step through T0–T6 or reverse a microcycle.","چرخه‌های T0 تا T6 را اجرا یا یک ریزچرخه را واگرد کنید."),"SC timing control bus T0 T1"),
    Tool("debugger",6,"computer","debugger",("Assembler & debugger","اسمبلر و اشکال‌زدا"),("Assemble an example, set a breakpoint and reverse execution.","یک مثال را اسمبل کنید، نقطه توقف بگذارید و اجرا را واگرد کنید."),"ASM assembly breakpoint"),
    Tool("microprogram",7,"computer","microprogram",("Microprogram control store","حافظه کنترل ریزبرنامه"),("Load a symbolic or raw microprogram and step its sequencer.","ریزبرنامه نمادین یا خام را بارگذاری و اجرا کنید."),"CAR SBR microcode"),
    Tool("microbuilder",7,"computer","microbuilder",("Microinstruction builder","سازنده ریزدستور"),("Choose F1/F2/F3 and branch fields; inspect the encoded word.","فیلدهای F1/F2/F3 و پرش را انتخاب و کلمه کدشده را بررسی کنید."),"F1 F2 F3 CD BR AD"),
    Tool("general-registers",8,"computer","general-registers",("General register organization","سازمان ثبات‌های عمومی"),("Build a control word and apply an ALU transfer.","کلمه کنترل بسازید و انتقال ALU را اعمال کنید."),"SELA SELB SELD OPR"),
    Tool("stacks",8,"computer","stacks",("Register & memory stacks","پشته ثباتی و حافظه‌ای"),("Compare PUSH/POP and stack pointer boundaries.","PUSH/POP و مرزهای اشاره‌گر پشته را مقایسه کنید."),"SP FULL EMPTY"),
    Tool("addressing",8,"computer","addressing",("Addressing modes","حالت‌های آدرس‌دهی"),("Calculate an effective address and inspect memory reads.","آدرس مؤثر را محاسبه و خواندن حافظه را بررسی کنید."),"EA direct indirect relative indexed"),
    Tool("formats",8,"computer","formats",("Instruction formats & postfix","قالب دستور و پسوندی"),("Compare zero-, one-, two- and three-address evaluation.","محاسبه صفر، یک، دو و سه‌آدرسی را مقایسه کنید."),"postfix infix RPN"),
    Tool("pipeline",9,"computer","pipeline",("Instruction pipeline","خط لوله دستورات"),("Compare forwarding, shared-port stalls and branch prediction.","ارسال مستقیم، توقف درگاه مشترک و پیش‌بینی پرش را مقایسه کنید."),"IF ID EX MEM WB RAW hazard"),
    Tool("vector",9,"computer","vector",("Vector & matrix arithmetic","محاسبات بردار و ماتریس"),("Compare arithmetic pipeline cycles and matrix results.","چرخه‌های خط لوله محاسباتی و نتایج ماتریس را مقایسه کنید."),"MAC dot matrix SIMD"),
    Tool("floating-pipeline",9,"computer","floating-pipeline",("Floating-point pipeline","خط لوله ممیز شناور"),("Inspect exponent alignment and binary16 rounding stages.","هم‌ترازی نما و مراحل گردکردن binary16 را بررسی کنید."),"IEEE binary16 float"),
    Tool("booth",10,"computer","booth",("Booth multiplication","ضرب بوث"),("Inspect signed multiplication steps.","مراحل ضرب علامت‌دار را بررسی کنید."),"Booth multiplication"),
    Tool("division",10,"computer","division",("Restoring & non-restoring division","تقسیم بازگرداننده و غیربازگرداننده"),("Choose a division algorithm and inspect quotient/remainder.","الگوریتم تقسیم را انتخاب و خارج‌قسمت و باقیمانده را بررسی کنید."),"divide division restoring"),
    Tool("decimal",10,"computer","decimal",("Packed decimal arithmetic","محاسبات ده‌دهی فشرده"),("Inspect BCD correction and decimal carry.","اصلاح BCD و نقلی ده‌دهی را بررسی کنید."),"BCD decimal"),
    Tool("floating",10,"computer","floating",("Binary16 floating-point arithmetic","محاسبات ممیز شناور binary16"),("Inspect IEEE binary16 encoding, rounding and special values.","کدگذاری، گردکردن و مقادیر ویژه binary16 را بررسی کنید."),"IEEE floating NaN infinity"),
    Tool("handshake",11,"computer","handshake",("Asynchronous handshake","دست‌دهی ناهمگام"),("Follow VALID/READY and capture one byte.","سیگنال‌های VALID/READY را دنبال و یک بایت دریافت کنید."),"I/O asynchronous"),
    Tool("interrupt",11,"computer","interrupt",("Priority interrupt","وقفه اولویت‌دار"),("Mask requests, acknowledge a winner and return with EOI.","درخواست‌ها را ماسک کنید، وقفه را تأیید و با EOI بازگردید."),"IRQ IEN daisy chain"),
    Tool("dma",11,"computer","dma",("Direct memory access","دسترسی مستقیم حافظه"),("Compare burst and cycle-stealing transfers and completion IRQ.","انتقال بلوکی و سرقت چرخه و وقفه پایان را مقایسه کنید."),"DMA BR BG"),
    Tool("fifo",11,"computer","fifo",("Circular FIFO","صف حلقوی FIFO"),("Fill, read and exchange words while tracking pointers.","صف را پر کنید، بخوانید و اشاره‌گرها را دنبال کنید."),"FIFO queue RP WP"),
    Tool("memory-chip",12,"logic","memory-chip",("RAM & ROM chips","تراشه‌های RAM و ROM"),("Inspect select, output and write enable controls.","کنترل انتخاب، فعال‌سازی خروجی و نوشتن را بررسی کنید."),"RAM ROM CS OE WE"),
    Tool("memory-array",12,"logic","memory-array",("Memory expansion","گسترش حافظه"),("Combine depth banks and parallel word lanes.","بانک‌های عمقی و مسیرهای موازی کلمه را ترکیب کنید."),"memory bank"),
    Tool("interleaving",12,"computer","interleaving",("Memory interleaving","حافظه درهم‌تنیده"),("Compare consecutive and strided bank access timing.","زمان‌بندی دسترسی متوالی و گام‌دار بانک‌ها را مقایسه کنید."),"bank conflict stride"),
    Tool("multiprocessor",13,"computer","multiprocessor",("Shared bus arbitration","داوری گذرگاه مشترک"),("Compare fixed and rotating priority with queued read/write requests.","اولویت ثابت و چرخشی را با درخواست‌های خواندن و نوشتن مقایسه کنید."),"multiprocessor arbitration round robin shared bus"),
)
BY_ID={tool.id:tool for tool in TOOLS}
BY_CHAPTER={chapter.number:chapter for chapter in CHAPTERS}


def normalize(text):
    text=unicodedata.normalize("NFKC",text).casefold().translate(str.maketrans("يك","یک"))
    text=text.replace("\u200c"," ").replace("\u200d"," ")
    return " ".join(text.split())


def search_tools(query="",chapter=0,practiced=(),remaining=False):
    terms=normalize(query).split()
    practiced=set(practiced)
    result=[]
    for tool in TOOLS:
        if chapter and chapter!=tool.chapter:continue
        if remaining and tool.id in practiced:continue
        section=BY_CHAPTER[tool.chapter]
        haystack=normalize(" ".join((tool.id,*tool.title,*tool.task,tool.keywords,*section.title,str(section.number))))
        if all(term in haystack for term in terms):result.append(tool)
    return tuple(result)


def clean_progress(values):
    return tuple(sorted(set(v for v in values if isinstance(v,str) and v in BY_ID)))
