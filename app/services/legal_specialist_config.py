"""
Comprehensive Legal Specialist Configuration
Contains all keywords, concepts, descriptions, subcategory explanations, and context for legal analysis agents
Organized according to US legal practice areas and statutes
"""

# Legal Area Definitions according to US Law
LEGAL_AREA_DEFINITIONS = {
    "Family Law": "Legal matters involving family relationships under state domestic relations law, including marriage dissolution under no-fault divorce statutes, child custody under best interests standards, adoption proceedings under state adoption codes, domestic relations governed by family courts, and family-related disputes under applicable state family law statutes. Governs legal rights and obligations between family members including marital dissolution, parental rights under constitutional due process, child welfare under state protection statutes, guardianship under probate codes, and spousal support under state maintenance guidelines.",
    
    "Employment Law": "Legal matters involving employer-employee relationships under federal and state labor law, including workplace rights under Title VII, Americans with Disabilities Act, Age Discrimination in Employment Act, Fair Labor Standards Act, employment contracts under state contract law, discrimination under federal civil rights statutes, harassment under EEOC guidelines, wrongful termination under state employment law, wages under federal and state wage and hour laws, and workplace conditions under OSHA regulations. Covers both statutory employment protections under federal civil rights laws and contractual employment relationships under state contract law, workplace safety under occupational safety statutes, labor disputes under National Labor Relations Act, and employment benefits under ERISA.",
    
    "Criminal Law": "Legal matters involving violations of federal and state criminal statutes, including arrests under Fourth Amendment protections, criminal charges under state penal codes, criminal proceedings under constitutional due process requirements, and defense against criminal allegations under Sixth Amendment right to counsel. Covers felonies and misdemeanors under state criminal codes, federal crimes under U.S. Criminal Code, criminal violations prosecuted by state and federal prosecutors, including constitutional rights under Bill of Rights, criminal procedure under Federal Rules of Criminal Procedure and state equivalents, plea negotiations under federal and state plea bargaining practices, and sentencing under federal sentencing guidelines and state sentencing statutes.",
    
    "Real Estate Law": "Legal matters involving real property under state real property law, including real estate transactions under state real estate statutes, ownership rights under property law, property disputes under state civil procedure, real estate contracts under state contract law and Statute of Frauds requirements, mortgages under state mortgage law and federal lending regulations, foreclosures under state foreclosure statutes and federal mortgage regulations, and property development under local zoning ordinances. Governs rights and obligations related to real property under state property codes, including title issues under state recording statutes, zoning under local municipal codes, construction disputes under state construction lien laws, and landlord-tenant relationships when involving property ownership under state landlord-tenant statutes.",
    
    "Business/Corporate Law": "Legal matters involving business operations under state corporation codes and federal securities law, including commercial transactions under Uniform Commercial Code, corporate governance under state business entity statutes, business contracts under state contract law, partnerships under state partnership acts, business disputes under state and federal commercial law, and commercial relationships under UCC and federal trade regulation. Includes entertainment industry contracts under state contract law and federal copyright/trademark law, professional service agreements under state professional licensing codes, corporate compliance under federal securities regulations and state corporate law, mergers and acquisitions under federal securities law and state corporate codes, and commercial litigation under state civil procedure and federal commercial law.",
    
    "Immigration Law": "Legal matters involving immigration status under federal Immigration and Nationality Act, visa applications under federal immigration regulations, deportation proceedings under federal immigration law, citizenship under federal naturalization law, asylum under federal refugee and asylum law, and immigration-related proceedings before federal immigration courts and agencies under Department of Homeland Security regulations. Covers removal defense under federal immigration court procedures, family-based immigration under federal immigration preference system, employment-based visas under federal immigration law, and naturalization processes under federal citizenship requirements and procedures.",
    
    "Personal Injury Law": "Legal matters involving physical injuries under state tort law, including medical malpractice under state medical malpractice statutes, accidents under state negligence law, negligence claims under common law tort principles, and compensation for personal injuries under state damage statutes caused by others' actions or negligence under duty of care standards. Includes motor vehicle accidents under state motor vehicle codes and insurance regulations, premises liability under state property owner liability law, product liability under state strict liability and negligence law, and professional malpractice under state professional liability standards resulting in physical harm under state personal injury statutes.",
    
    "Wills, Trusts, & Estates Law": "Legal matters involving estate planning under state probate codes, probate proceedings under state probate court jurisdiction, will contests under state will contest statutes, trust administration under state trust law and Uniform Trust Code, inheritance under state intestacy statutes, and posthumous asset distribution under state estate administration law. Governs transfer of assets upon death or incapacity under state probate and trust law, including will drafting under state will execution requirements, trust creation under state trust formation law, estate administration under state probate procedures, and probate disputes under state probate court rules and procedures.",
    
    "Bankruptcy, Finances, & Tax Law": "Legal matters involving debt relief under federal Bankruptcy Code, bankruptcy proceedings under federal bankruptcy court jurisdiction, tax disputes under federal tax law and state tax codes, financial restructuring under federal bankruptcy law, creditor-debtor relationships under state debtor-creditor law and federal bankruptcy law, and tax compliance or disputes with federal and state tax authorities under applicable tax codes. Includes consumer bankruptcy under Chapters 7 and 13 of Bankruptcy Code, business restructuring under Chapter 11 of Bankruptcy Code, tax planning under federal Internal Revenue Code and state tax law, and IRS proceedings under federal tax procedure and administration statutes.",
    
    "Government & Administrative Law": "Legal matters involving government agencies under federal and state administrative law, administrative proceedings under Administrative Procedure Act and state administrative codes, government benefits under federal entitlement programs and state benefit systems, regulatory compliance under federal and state regulatory schemes, administrative appeals under federal and state administrative procedure, and disputes with government entities under federal and state administrative law and civil rights statutes. Includes Social Security disability under federal Social Security Act, veterans benefits under federal veterans' benefits law, licensing issues under state professional licensing codes, and regulatory enforcement under applicable federal and state regulatory statutes.",
    
    "Product & Services Liability Law": "Legal matters involving defective products under state product liability law and federal consumer protection statutes, service failures under state contract and tort law, consumer protection under federal consumer protection acts and state consumer fraud statutes, professional malpractice under state professional liability law, warranties under Uniform Commercial Code and federal warranty law, and liability for products or services under state strict liability and negligence law that cause harm or fail to perform as expected under contract and warranty law. Includes product safety under federal consumer product safety regulations, consumer fraud under state consumer protection acts and federal FTC regulations, and professional negligence under state professional standards and malpractice law.",
    
    "Intellectual Property Law": "Legal matters involving patents under federal Patent Act, copyrights under federal Copyright Act, trademarks under federal Trademark Act (Lanham Act), trade secrets under state trade secret law and federal Defend Trade Secrets Act, and other intellectual property rights under federal intellectual property law, including infringement claims under federal IP statutes and IP protection under federal registration and enforcement systems. Covers creative works under federal copyright law, inventions under federal patent law, brand protection under federal trademark law, and technology licensing under federal and state intellectual property licensing law.",
    
    "Landlord/Tenant Law": "Legal matters involving rental relationships under state landlord-tenant law, lease agreements under state real property and contract law, eviction proceedings under state unlawful detainer statutes, habitability issues under state warranty of habitability law, rent disputes under state rent regulation and landlord-tenant codes, and rights and obligations between landlords and tenants under state residential and commercial landlord-tenant statutes. Covers residential and commercial leasing under state real property law, housing code violations under local housing codes and state habitability standards, and rental property management under state property management and landlord-tenant regulations."
}

# Detailed Subcategory Explanations According to US Law - CRYSTAL CLEAR DISTINCTIONS
SUBCATEGORY_EXPLANATIONS = {
    "Family Law": {
        "Adoptions": "ONLY legal proceedings under state adoption codes (UCC Article 9) to permanently transfer parental rights and establish new parent-child relationships. Includes: stepparent adoptions under expedited state procedures, agency adoptions through state-licensed agencies, private adoptions with birth parent consent under state requirements, international adoptions under Hague Adoption Convention and Immigration and Nationality Act, adult adoptions under simplified state procedures, and contested adoptions requiring involuntary termination of parental rights under state child protection statutes with clear and convincing evidence standard. EXCLUDES: guardianship (temporary authority), custody (existing parent-child relationships), or foster care arrangements.",
        
        "Child Custody & Visitation": "EXCLUSIVELY determination of legal custody (decision-making authority) and physical custody (residential arrangements) under state custody statutes applying best interests standard from existing parent-child relationships. Covers: initial custody determinations in divorce or paternity actions, joint legal/physical custody under state joint custody statutes, sole custody with visitation schedules, supervised visitation under court orders, custody modifications under substantial change of circumstances standard, interstate custody under Uniform Child Custody Jurisdiction and Enforcement Act (UCCJEA), and custody enforcement through contempt of court. EXCLUDES: adoption proceedings, guardianship of non-parents, or child support calculations.",
        
        "Child Support": "SPECIFICALLY financial support obligations between parents under state child support guidelines implementing federal Child Support Enforcement Act (42 USC 651). Limited to: initial child support calculations using state income shares or percentage of income models, modification petitions based on substantial change in circumstances (typically 15% deviation), enforcement actions including wage garnishment under Consumer Credit Protection Act, asset seizure, license suspension, and contempt proceedings, interstate enforcement under Uniform Interstate Family Support Act (UIFSA), medical support obligations, and arrears collection. EXCLUDES: spousal support, adoption costs, or general child welfare matters.",
        
        "Divorce": "SOLELY marital dissolution proceedings under state divorce statutes terminating valid marriages. Encompasses: contested divorce with disputed issues, uncontested divorce with settlement agreements, no-fault divorce under irreconcilable differences, fault-based divorce where available under state law, property division under equitable distribution (majority states) or community property (9 states) principles, temporary orders during pendency, divorce mediation and collaborative divorce alternatives, and entry of final divorce decree dissolving marriage. EXCLUDES: legal separation (marriage remains), annulment (void marriage), or unmarried partnership dissolution.",
        
        "Guardianship": "EXCLUSIVELY court-appointed legal authority over persons or estates under state guardianship/conservatorship statutes when individual lacks capacity. Covers: guardianship of minors when parents deceased, incapacitated, or absent, adult guardianship for incapacitated persons under state incapacity standards with due process protections, limited guardianship with restricted powers, temporary/emergency guardianships under expedited procedures, guardianship accounting and annual reporting to probate court, and termination when capacity restored or circumstances change. EXCLUDES: adoption (permanent parental rights), custody (between parents), or power of attorney (voluntary arrangements).",
        
        "Paternity": "STRICTLY legal establishment or disestablishment of biological father-child relationships under state paternity statutes for unmarried parents. Includes: voluntary acknowledgment of paternity under state administrative procedures, contested paternity actions with court-ordered genetic testing under 99% probability standard, disestablishment of paternity based on fraud, duress, or material mistake of fact, paternity determinations for child support and custody purposes, paternity involving assisted reproductive technology under state ART laws, and interstate paternity under UIFSA. EXCLUDES: custody arrangements (separate proceeding), adoption by stepfathers, or marital presumption cases.",
        
        "Separations": "ONLY legal separation proceedings under state separation statutes maintaining marital status while addressing support and property. Covers: legal separation petitions as alternative to divorce, separation agreements addressing property division and spousal/child support, conversion of separation to divorce after waiting periods, temporary separation orders during divorce proceedings, and enforcement of separation agreements under contract law principles. EXCLUDES: informal separations, divorce proceedings (terminates marriage), or post-divorce modifications.",
        
        "Spousal Support or Alimony": "EXCLUSIVELY financial support obligations between current or former spouses under state spousal maintenance statutes. Limited to: temporary spousal support during divorce proceedings, permanent spousal support based on need, ability to pay, and statutory factors, rehabilitative alimony for specific time periods, modification petitions based on substantial change in circumstances, termination upon recipient's remarriage or cohabitation under state law, and enforcement through contempt, wage garnishment, and asset seizure. EXCLUDES: child support obligations, property division, or support between unmarried partners."
    },
    
    "Employment Law": {
        "Disabilities": "EXCLUSIVELY workplace disability discrimination and accommodation under Americans with Disabilities Act (42 USC 12101) and state disability rights laws. Covers ONLY: reasonable accommodation requests for qualified individuals with disabilities, interactive accommodation process requirements, undue hardship defenses by employers, disability discrimination in hiring, promotion, termination, and conditions of employment, medical examination and inquiry restrictions under ADA, disability-related harassment creating hostile work environment, and ADA compliance violations. EXCLUDES: workers' compensation (separate system), Social Security disability (federal benefits), or general medical leave requests.",
        
        "Employment Contracts": "STRICTLY contractual employment relationships under state contract law beyond at-will employment. Limited to: written employment agreements with specific terms and duration, executive compensation and severance packages, non-compete agreements under state restrictive covenant laws, non-disclosure and confidentiality agreements, employment contract breach claims and remedies, contract modification and termination procedures, restrictive covenant enforcement and reasonableness standards, and employment contract negotiations. EXCLUDES: at-will employment issues, statutory employment rights, or collective bargaining agreements.",
        
        "Employment Discrimination": "SOLELY discrimination based on protected characteristics under federal civil rights laws: Title VII (race, color, religion, sex, national origin), Age Discrimination in Employment Act (40+ years), Americans with Disabilities Act (disability), and state anti-discrimination statutes. Covers: discriminatory hiring, promotion, termination, and employment terms, disparate treatment and disparate impact theories, pattern and practice discrimination, class action discrimination claims, EEOC complaint procedures and right-to-sue letters, and discrimination remedies including reinstatement and damages. EXCLUDES: disability accommodation (separate category), harassment (separate category), or contractual disputes.",
        
        "Pensions and Benefits": "EXCLUSIVELY employee benefit plans under Employee Retirement Income Security Act (ERISA, 29 USC 1001) and state benefit laws. Covers: pension plan administration and fiduciary breaches, 401(k) and retirement benefit disputes, health insurance coverage under ERISA, COBRA continuation coverage rights, benefit plan document interpretation, benefit claim denials and ERISA appeals procedures, fiduciary duty violations by plan administrators, and benefit plan participant rights. EXCLUDES: workers' compensation, unemployment benefits, or general employment terms.",
        
        "Sexual Harassment": "SPECIFICALLY unwelcome sexual conduct under Title VII creating quid pro quo or hostile work environment. Limited to: quid pro quo harassment by supervisors conditioning employment on sexual favors, hostile work environment from pervasive sexual conduct, employer liability under Ellerth/Faragher standards, harassment by supervisors, co-workers, and third parties, employer anti-harassment policy requirements, harassment investigation and response obligations, and retaliation against harassment complainants under Title VII. EXCLUDES: non-sexual harassment, general discrimination, or workplace bullying without sexual content.",
        
        "Wages and Overtime Pay": "EXCLUSIVELY wage and hour violations under Fair Labor Standards Act (29 USC 201) and state wage laws. Covers: minimum wage violations for covered employees, overtime compensation for non-exempt employees exceeding 40 hours weekly, meal and rest break requirements under state law, final paycheck timing and content requirements, wage statement and record-keeping obligations, prevailing wage requirements for public works under Davis-Bacon Act, and collective wage theft claims. EXCLUDES: salary disputes under contracts, commission payment disputes, or general compensation disagreements.",
        
        "Workplace Disputes": "NARROWLY employment-related conflicts under federal and state employment law NOT covered by other subcategories. Includes: workplace policy enforcement and violations, employee handbook interpretation, disciplinary actions and performance evaluations, workplace safety complaints under Occupational Safety and Health Act, internal grievance procedures and dispute resolution, workplace accommodation requests (non-disability), and employment-related alternative dispute resolution. EXCLUDES: discrimination, harassment, wage violations, or contractual disputes (each has separate categories).",
        
        "Wrongful Termination": "SPECIFICALLY unlawful discharge under federal and state employment law exceptions to at-will employment. Covers: termination violating public policy (whistleblowing, jury duty, workers' compensation claims), discriminatory discharge under civil rights laws, retaliatory termination for protected activities, constructive discharge creating intolerable working conditions, breach of implied employment contract, termination violating express employment agreements, and wrongful discharge in violation of state wrongful termination statutes. EXCLUDES: layoffs for economic reasons, termination for cause, or general employment disputes."
    },
    
    "Criminal Law": {
        "General Criminal Defense": "BROADLY criminal defense representation under state and federal criminal codes for serious charges requiring comprehensive legal strategy. Covers: felony defense involving potential imprisonment exceeding one year, complex criminal cases with multiple charges or defendants, federal criminal defense under U.S. Criminal Code (Title 18), constitutional rights protection including Fourth, Fifth, and Sixth Amendment violations, plea negotiation for serious charges, criminal trial advocacy and jury selection, sentencing advocacy under federal guidelines or state sentencing statutes, post-conviction relief and appeals, and pre-trial detention and bail proceedings. EXCLUDES: simple traffic violations, minor misdemeanors, or specialized crime categories below.",
        
        "Environmental Violations": "EXCLUSIVELY criminal enforcement of environmental protection laws under federal environmental statutes. Limited to: Clean Air Act criminal violations (42 USC 7413), Clean Water Act criminal violations (33 USC 1319), Resource Conservation and Recovery Act criminal violations (42 USC 6928), Comprehensive Environmental Response Act (CERCLA) criminal violations, toxic substance control violations, environmental permit violations with criminal penalties, corporate environmental criminal liability, and knowing endangerment charges under environmental statutes. EXCLUDES: civil environmental violations, regulatory compliance matters, or other criminal charges.",
        
        "Drug Crimes": "SPECIFICALLY controlled substance offenses under Controlled Substances Act (21 USC 801) and state drug laws. Covers: drug possession charges under federal and state schedules, drug trafficking and distribution under federal sentencing guidelines, drug manufacturing and cultivation offenses, prescription drug fraud and illegal distribution, drug conspiracy charges under federal conspiracy law, asset forfeiture in drug cases under civil and criminal forfeiture statutes, drug court participation and treatment alternatives, and RICO violations involving drug enterprises. EXCLUDES: DUI/alcohol offenses, other criminal charges, or civil drug matters.",
        
        "Drunk Driving/DUI/DWI": "SOLELY impaired driving offenses under state motor vehicle codes and implied consent laws. Limited to: DUI/DWI charges based on blood alcohol content above state limits (typically 0.08%), field sobriety test administration and challenges, chemical testing (breath, blood, urine) and refusal consequences, administrative license suspension and DMV hearings, repeat offender penalties and enhanced sentences, ignition interlock device requirements, DUI-related vehicular homicide and assault charges, and commercial driver DUI violations. EXCLUDES: other traffic violations, drug crimes, or general criminal charges.",
        
        "Felonies": "EXCLUSIVELY serious criminal offenses under state and federal law punishable by imprisonment exceeding one year in state prison or federal penitentiary. Covers: violent felonies including murder, rape, robbery, aggravated assault, property felonies including burglary, grand theft, arson, white collar felonies including fraud, embezzlement, money laundering, drug felonies under controlled substance laws, federal crimes under U.S. Criminal Code, three strikes laws and habitual offender enhancement, federal sentencing guidelines application, and post-conviction consequences including civil disabilities. EXCLUDES: misdemeanor charges, traffic violations, or civil matters.",
        
        "Misdemeanors": "SPECIFICALLY lesser criminal offenses under state criminal codes punishable by fines and imprisonment up to one year in county jail. Covers: summary offenses and violations, misdemeanor assault and battery, petty theft and shoplifting under state theft thresholds, disorderly conduct and public nuisance charges, criminal trespass and minor property crimes, domestic violence misdemeanors under state domestic violence laws, and traffic-related criminal violations beyond simple infractions. EXCLUDES: felony charges, serious traffic violations (DUI), or civil infractions.",
        
        "Speeding and Moving Violations": "EXCLUSIVELY traffic violations under state motor vehicle codes not involving impairment. Limited to: speeding violations and speed contest charges, reckless driving under state reckless driving statutes, careless driving and following too closely, improper lane changes and unsafe driving, running red lights and stop signs, commercial driving violations under Commercial Motor Vehicle Safety Act, license points accumulation and suspension consequences, and traffic violation defenses. EXCLUDES: DUI/DWI (separate category), vehicular homicide (felony), or other criminal charges.",
        
        "White Collar Crime": "SPECIFICALLY financial and business crimes under federal and state criminal law involving fraud or breach of trust. Covers: securities fraud under federal securities laws (15 USC 78ff), wire and mail fraud (18 USC 1341, 1343), embezzlement and theft of funds, money laundering under Bank Secrecy Act (31 USC 5322), computer crimes and identity theft under federal computer fraud laws, bankruptcy fraud, healthcare fraud under federal healthcare fraud statutes, tax evasion (criminal), and corporate criminal liability. EXCLUDES: violent crimes, drug offenses, or regulatory violations without criminal intent.",
        
        "Tax Evasion": "EXCLUSIVELY criminal tax violations under Internal Revenue Code (26 USC 7201-7217) and state tax criminal statutes. Limited to: willful tax evasion under 26 USC 7201, tax fraud and false returns under 26 USC 7206, failure to file tax returns under 26 USC 7203, employment tax violations and payroll tax crimes, tax shelter abuse and promotional schemes, criminal tax investigations by IRS Criminal Investigation Division, voluntary disclosure programs and cooperation agreements, and criminal tax penalties and prosecution procedures. EXCLUDES: civil tax disputes, tax collection matters, or other financial crimes."
    },
    
    "Real Estate Law": {
        "Commercial Real Estate": "EXCLUSIVELY commercial property transactions and disputes under state real estate law involving business properties. Covers: commercial purchase and sale agreements under state real estate statutes, commercial lease negotiations and disputes (office, retail, industrial), commercial property development and zoning compliance, commercial real estate financing and loan agreements, environmental due diligence for commercial properties, commercial property tax assessment and appeals, commercial real estate investment transactions, and commercial landlord-tenant law. EXCLUDES: residential property matters, single-family home transactions, or residential landlord-tenant issues.",
        
        "Condominiums and Cooperatives": "SPECIFICALLY multi-unit ownership under state condominium and cooperative laws and Uniform Common Interest Ownership Act. Limited to: condominium association governance and bylaw enforcement, cooperative board decisions and shareholder rights under proprietary leases, common area maintenance and repair obligations, special assessment collection and lien enforcement, condominium and cooperative conversion under state conversion statutes, homeowner association law and CC&R enforcement, and common interest community disputes. EXCLUDES: single-family homes, rental properties, or general property ownership issues.",
        
        "Construction Disputes": "EXCLUSIVELY construction-related legal issues under state construction and mechanic's lien laws. Covers: construction contract disputes and breach of construction agreements, construction defect claims under state construction defect statutes, mechanic's liens and material supplier liens under state lien laws, construction bond claims and surety bond enforcement, construction delay claims and cost overrun disputes, construction licensing and contractor regulation violations, construction accident liability and premises liability, and architect/engineer professional liability. EXCLUDES: general property disputes, real estate transactions, or non-construction related matters.",
        
        "Foreclosures": "SOLELY mortgage foreclosure proceedings under state foreclosure statutes and federal mortgage regulations. Limited to: judicial foreclosure proceedings in court systems, non-judicial foreclosure under deed of trust procedures, foreclosure defense and loss mitigation negotiations, short sales and deeds in lieu of foreclosure, foreclosure sale procedures and confirmation, redemption rights under state redemption statutes, deficiency judgment actions and anti-deficiency protections, and federal mortgage modification programs (HAMP, HARP). EXCLUDES: mortgage origination issues, general loan disputes, or property ownership matters.",
        
        "Mortgages": "SPECIFICALLY real estate financing under state mortgage law, federal lending regulations, and Truth in Lending Act. Covers: mortgage origination and closing issues, mortgage modification and refinancing procedures, predatory lending claims under federal and state consumer protection laws, mortgage broker and lender liability under Real Estate Settlement Procedures Act (RESPA), mortgage insurance disputes and claims, compliance with federal mortgage lending laws (Dodd-Frank, TILA), and mortgage servicing and payment processing issues. EXCLUDES: foreclosure proceedings (separate category), general banking matters, or non-real estate loans.",
        
        "Purchase and Sale of Residence": "EXCLUSIVELY residential real estate transactions under state real estate law and regulations. Covers: residential purchase agreements and contract interpretation, title examinations and title insurance claims, property inspection contingencies and disclosure requirements under state disclosure laws, real estate closing procedures and document preparation, buyer and seller representation under state real estate licensing law, earnest money and escrow disputes, and post-closing warranty and disclosure violation claims. EXCLUDES: commercial property, foreclosure sales, or landlord-tenant matters.",
        
        "Title and Boundary Disputes": "SPECIFICALLY real property ownership and boundary issues under state real property law. Limited to: title defects and clouds on title requiring quiet title actions, boundary line disputes and adverse possession claims, easement creation, interpretation, and termination under easement law, property encroachment issues and trespass claims, survey disputes and surveyor liability, property description and deed interpretation problems, and title insurance coverage disputes and claims. EXCLUDES: landlord-tenant disputes, construction issues, or general property damage claims."
    },
    
    "Business/Corporate Law": {
        "Breach of Contract": "EXCLUSIVELY contract disputes under state contract law involving commercial agreements and business relationships. Covers: breach of commercial contracts including supply, distribution, and service agreements, material breach and substantial performance analysis under contract law, contract interpretation and ambiguous terms, specific performance and monetary damages remedies, anticipatory breach and repudiation, contract modification and waiver issues, third-party beneficiary and assignment disputes, and commercial contract alternative dispute resolution. EXCLUDES: employment contracts (separate category), real estate contracts, or consumer contracts.",
        
        "Corporate Tax": "SPECIFICALLY business taxation under Internal Revenue Code Subchapter C and state corporate tax codes. Limited to: corporate income tax compliance and planning, tax planning for mergers and acquisitions under IRC Section 368, business entity tax elections (S-Corp, LLC), international business taxation and transfer pricing, corporate tax controversy and IRS audits, state and local business taxation including franchise taxes, tax-efficient business structure planning, and corporate tax penalties and interest disputes. EXCLUDES: individual tax matters, employment tax issues, or estate tax planning.",
        
        "Business Disputes": "BROADLY commercial litigation under state business law NOT covered by other subcategories. Covers: partnership and LLC disputes under state partnership and LLC acts, shareholder and corporate governance disputes, breach of fiduciary duty claims by officers and directors, business torts including unfair competition and trade secret misappropriation, commercial fraud and business misrepresentation, business relationship dissolution and wind-up procedures, and business valuation and buy-out disputes. EXCLUDES: contract breaches (separate category), employment disputes, or intellectual property matters.",
        
        "Buying and Selling a Business": "EXCLUSIVELY business acquisition transactions under state business entity law and federal securities regulations. Covers: asset purchase agreements and due diligence procedures, stock purchase agreements and representations/warranties, merger and acquisition transactions under state corporate law, business valuation and purchase price adjustments, regulatory approvals and Hart-Scott-Rodino filings, financing arrangements and escrow agreements, post-closing integration and indemnification disputes, and business succession planning. EXCLUDES: general business disputes, ongoing business operations, or employment matters.",
        
        "Contract Drafting and Review": "SPECIFICALLY preparation and analysis of commercial agreements under state contract law principles. Limited to: service agreements and professional services contracts, supply and distribution agreement drafting, licensing and technology agreement preparation, vendor and customer contract negotiations, confidentiality and non-disclosure agreement drafting, terms and conditions development, contract risk allocation and limitation of liability clauses, and commercial contract template development. EXCLUDES: contract disputes (separate category), employment agreements, or real estate contracts.",
        
        "Corporations, LLCs, Partnerships, etc.": "EXCLUSIVELY business entity formation, governance, and compliance under state business entity statutes. Covers: corporate formation and articles of incorporation under state corporation codes, LLC operating agreement drafting under state LLC acts, partnership agreement preparation under Uniform Partnership Act, corporate governance and board of directors compliance, business entity annual filings and state compliance, entity restructuring and conversions, corporate bylaws and governance documents, and business entity dissolution procedures. EXCLUDES: business disputes (separate category), tax matters, or operational contracts.",
        
        "Entertainment Law": "SPECIFICALLY entertainment industry legal matters under federal copyright/trademark law and state contract law. Limited to: talent representation agreements and artist management contracts, production and distribution agreements for film/television/music, intellectual property licensing for entertainment content, entertainment financing and investment agreements, music recording and publishing contracts, performer and athlete contracts, entertainment industry labor issues, and entertainment-related litigation and disputes. EXCLUDES: general business contracts, employment law matters, or non-entertainment intellectual property."
    },
    
    "Immigration Law": {
        "Citizenship": "EXCLUSIVELY U.S. citizenship acquisition under Immigration and Nationality Act Section 316-322 and naturalization procedures. Covers: naturalization applications (Form N-400) and eligibility requirements, citizenship through parents under INA Section 320-322, citizenship test preparation and civics/English requirements, dual citizenship issues and renunciation procedures, oath of allegiance ceremonies and naturalization delays, citizenship denial appeals and administrative review, certificate of citizenship applications (Form N-600), and derived citizenship for children. EXCLUDES: lawful permanent residence applications, visa matters, or removal proceedings.",
        
        "Deportation": "SPECIFICALLY removal proceedings under Immigration and Nationality Act Section 240 before immigration courts. Limited to: removal defense strategies and deportation proceedings, cancellation of removal applications under INA Section 240A, asylum and withholding of removal claims in removal proceedings, appeals to Board of Immigration Appeals and federal court review, immigration detention and bond proceedings under INA Section 236, voluntary departure and stipulated removal orders, relief from removal including 212(h) waivers, and post-removal challenges. EXCLUDES: visa applications, citizenship matters, or immigration benefits outside removal context.",
        
        "Permanent Visas or Green Cards": "EXCLUSIVELY lawful permanent residence under Immigration and Nationality Act family and employment preference categories. Covers: family-based immigrant petitions (I-130) under INA Section 201-203, employment-based immigrant petitions (I-140) under INA Section 203(b), adjustment of status applications (I-485) under INA Section 245, consular processing abroad under INA Section 221, green card renewal and replacement (I-90), removal of conditions on permanent residence (I-751), and immigrant visa processing procedures. EXCLUDES: nonimmigrant visas (temporary), citizenship applications, or removal proceedings.",
        
        "Temporary Visas": "SPECIFICALLY nonimmigrant visas under Immigration and Nationality Act Section 101(a)(15) for temporary stay. Limited to: work visas including H-1B specialty occupation, L-1 intracompany transferee, O-1 extraordinary ability, student visas (F-1, M-1) under INA Section 101(a)(15)(F), visitor visas (B-1/B-2) for business and tourism, treaty trader/investor visas (E-1/E-2), visa extensions and changes of status (I-539), and temporary visa violations and consequences. EXCLUDES: permanent residence applications, asylum claims, or removal proceedings."
    },
    
    "Personal Injury Law": {
        "Automobile Accidents": "Motor vehicle accident liability under state tort law, including car accident injury claims, truck accident litigation, motorcycle accident cases, pedestrian and bicycle accident claims, uninsured and underinsured motorist coverage, hit-and-run accident claims, and wrongful death from vehicle accidents.",
        
        "Dangerous Property or Buildings": "Premises liability under state property law, including slip and fall accidents, inadequate security claims, building code violations, construction site accidents, swimming pool accidents, dog bite and animal attack cases, and property owner negligence and liability.",
        
        "Defective Products": "Product liability under state tort law, including design defect claims, manufacturing defect claims, warning and instruction defect claims, strict product liability, breach of warranty claims, mass tort and class action product cases, and product recall and safety issues.",
        
        "Medical Malpractice": "Healthcare professional liability under state medical malpractice law, including physician negligence, hospital liability, nursing home negligence, dental malpractice, pharmaceutical errors, surgical errors, misdiagnosis and delayed diagnosis, and birth injury and wrongful death claims.",
        
        "Personal Injury (General)": "General tort liability under state personal injury law, including negligence and premises liability claims, intentional tort claims, pain and suffering damages, economic loss recovery, personal injury settlement negotiations, and personal injury trial advocacy and litigation."
    },
    
    "Wills, Trusts, & Estates Law": {
        "Contested Wills or Probate": "Will contests and probate disputes under state probate law, including will validity challenges, undue influence and capacity claims, probate litigation and trials, estate administration disputes, beneficiary rights and remedies, and executor and administrator liability issues.",
        
        "Drafting Wills and Trusts": "Estate planning document preparation under state probate and trust law, including will drafting and execution, revocable living trust creation, irrevocable trust planning, power of attorney documents, advance healthcare directives, and estate planning for business owners and high net worth individuals.",
        
        "Estate Administration": "Probate and estate administration under state probate procedures, including probate court proceedings, asset inventory and valuation, creditor claims and debt payment, estate tax returns and compliance, estate distribution to beneficiaries, and estate accounting and reporting requirements.",
        
        "Estate Planning": "Comprehensive estate planning under federal estate tax law and state probate law, including tax-efficient estate planning strategies, charitable giving and philanthropy, business succession planning, family wealth preservation, trust administration and management, and elder law and long-term care planning."
    },
    
    "Bankruptcy, Finances, & Tax Law": {
        "Collections": "EXCLUSIVELY debt collection under Fair Debt Collection Practices Act (15 USC 1692) and state collection laws. Covers: creditor rights and collection remedies including wage garnishment, judgment collection and enforcement procedures, asset seizure and attachment under state execution laws, debtor exemptions under state and federal exemption statutes, collection defense and FDCPA violations, creditor-debtor negotiations and payment arrangements, collection agency regulation and licensing, and collection lawsuit defense. EXCLUDES: bankruptcy proceedings, tax collection, or consumer credit issues.",
        
        "Consumer Bankruptcy": "SPECIFICALLY individual bankruptcy under federal Bankruptcy Code Chapters 7 and 13. Limited to: Chapter 7 liquidation proceedings and discharge of debts, Chapter 13 wage earner repayment plans under 11 USC 1321-1330, bankruptcy exemptions under federal and state exemption schemes, automatic stay protection under 11 USC 362, means testing under Bankruptcy Abuse Prevention Act, reaffirmation agreements and redemption of secured property, bankruptcy discharge and non-dischargeable debts, and bankruptcy alternatives including debt counseling. EXCLUDES: business bankruptcy, tax matters, or general debt collection.",
        
        "Consumer Credit": "EXCLUSIVELY consumer credit transactions under federal consumer credit laws. Covers: Truth in Lending Act (TILA) violations and rescission rights, Fair Credit Reporting Act issues and credit report disputes, Equal Credit Opportunity Act discrimination claims, credit card disputes and billing error rights, predatory lending claims under federal and state laws, consumer loan and financing disputes, debt settlement and debt management services, and consumer credit counseling and education. EXCLUDES: bankruptcy proceedings, commercial credit, or debt collection actions.",
        
        "Income Tax": "SPECIFICALLY federal and state income tax matters under Internal Revenue Code and state tax codes. Limited to: income tax return preparation and compliance, tax audits and examinations by IRS and state agencies, tax controversy and appeals procedures, tax planning strategies and year-end planning, tax penalty and interest abatement requests, offer in compromise negotiations under IRC Section 7122, installment payment agreements under IRC Section 6159, and individual tax representation before tax authorities. EXCLUDES: business tax matters, estate tax, or criminal tax issues.",
        
        "Property Tax": "EXCLUSIVELY real property taxation under state and local tax assessment laws. Covers: property tax assessment appeals and valuation challenges, property tax exemptions including homestead and senior exemptions, property tax payment plans and deferrals, property tax liens and foreclosure proceedings, assessment uniformity and discrimination challenges, commercial property tax appeals and income approach valuations, and property tax compliance for multiple properties. EXCLUDES: income tax matters, sales tax, or other forms of taxation."
    },
    
    "Government & Administrative Law": {
        "Education and Schools": "EXCLUSIVELY educational law under federal and state education statutes and constitutional law. Covers: special education disputes under Individuals with Disabilities Education Act (IDEA) and Section 504, individualized education program (IEP) and 504 plan development and disputes, student discipline and due process under state education codes, school discrimination under Title IX and civil rights laws, teacher and staff employment under state education employment law, school board governance and open meeting law compliance, higher education issues including Title IX and student rights, and education funding and finance law. EXCLUDES: general employment law, civil rights outside education context, or administrative law not education-specific.",
        
        "Social Security – Disability": "SPECIFICALLY Social Security disability benefits under Social Security Act Title II (SSDI) and Title XVI (SSI). Limited to: initial disability applications (Forms SSA-1696, SSA-3368), disability appeals and administrative law judge hearings, medical evidence development and vocational assessments, disability claim representation before Social Security Administration, supplemental security income (SSI) eligibility and appeals, continuing disability reviews and cessation proceedings, work incentive programs and trial work periods, and federal court appeals under 42 USC 405(g). EXCLUDES: retirement benefits, Medicare issues, or other Social Security programs.",
        
        "Social Security – Retirement": "EXCLUSIVELY Social Security retirement benefits under Social Security Act Title II. Covers: retirement benefit applications and eligibility requirements, early retirement at age 62 and delayed retirement credits, spousal and divorced spouse benefits under Social Security Act, working during retirement and earnings test implications, Medicare enrollment coordination and timing, Social Security benefit calculations and Primary Insurance Amount, retirement benefit appeals and overpayment issues, and representative payee proceedings for incapacitated beneficiaries. EXCLUDES: disability benefits, survivor benefits, or Medicare coverage disputes.",
        
        "Social Security – Dependent Benefits": "SPECIFICALLY Social Security benefits for dependents under Social Security Act provisions. Limited to: child benefits for minor and disabled adult children, spousal benefits for current spouses under Social Security Act Section 202(b), divorced spouse benefits and duration requirements, student benefits and educational requirements where applicable, family maximum benefit calculations and reductions, dependent benefit termination and reinstatement, and coordination with other Social Security benefits. EXCLUDES: survivor benefits (separate category), retirement benefits, or disability determinations.",
        
        "Social Security – Survivor Benefits": "EXCLUSIVELY Social Security survivor benefits under Social Security Act Section 202. Covers: widow and widower benefits including early widow benefits, surviving divorced spouse benefits and marriage duration requirements, surviving child benefits and age/disability requirements, lump sum death payment eligibility and applications, mother's and father's benefits for surviving spouses with children, survivor benefit applications and appeals, remarriage effects on survivor benefits, and survivor benefit coordination with other benefits. EXCLUDES: retirement benefits, disability benefits, or life insurance matters.",
        
        "Veterans Benefits": "SPECIFICALLY veterans benefits under Title 38 USC and VA regulations. Limited to: disability compensation claims for service-connected disabilities, pension benefits for wartime veterans with financial need, healthcare benefits and medical treatment through VA system, education benefits under GI Bill and vocational rehabilitation, home loan guarantees under VA loan program, burial and cemetery benefits for veterans, dependency and indemnity compensation for survivors, and appeals to Board of Veterans' Appeals and Court of Appeals for Veterans Claims. EXCLUDES: military justice, civilian employment of veterans, or non-VA disability programs.",
        
        "General Administrative Law": "BROADLY administrative law proceedings under Administrative Procedure Act and state administrative codes NOT covered by specific subcategories above. Covers: professional licensing board proceedings and disciplinary actions, regulatory compliance and enforcement by government agencies, administrative rulemaking participation and challenges, agency adjudication and administrative hearings, appeals to superior courts from agency decisions, government contract disputes and procurement law, regulatory interpretation and advisory opinions, and administrative law judge proceedings. EXCLUDES: Social Security, veterans benefits, education law, or other specific administrative categories.",
        
        "Environmental Law": "EXCLUSIVELY environmental regulation and compliance under federal environmental statutes. Covers: Clean Air Act compliance and enforcement under 42 USC 7401, Clean Water Act permitting and violations under 33 USC 1251, hazardous waste regulation under Resource Conservation and Recovery Act, environmental impact assessments under National Environmental Policy Act, Superfund cleanup liability under Comprehensive Environmental Response Act, environmental permitting and licensing procedures, environmental enforcement actions and penalties, and environmental compliance auditing. EXCLUDES: criminal environmental violations (criminal law category), toxic torts, or natural resource damages.",
        
        "Liquor Licenses": "SPECIFICALLY alcoholic beverage licensing under state alcohol control laws and regulations. Limited to: liquor license applications and renewals under state alcoholic beverage control codes, license transfers and ownership changes, alcohol law compliance and regulatory violations, license suspension and revocation proceedings before alcohol control boards, representation at alcoholic beverage control hearings, zoning and land use issues for licensed premises, and alcohol manufacturer, distributor, and retailer licensing. EXCLUDES: DUI/criminal charges, general business licensing, or non-alcohol regulatory matters.",
        
        "Constitutional Law": "EXCLUSIVELY constitutional rights and government power under U.S. Constitution and state constitutions. Covers: civil rights violations under 42 USC 1983 and constitutional amendments, due process and equal protection claims under Fourteenth Amendment, First Amendment free speech, religion, and assembly rights, Fourth Amendment search and seizure violations, government liability and qualified immunity defenses, constitutional challenges to laws and regulations, voting rights under constitutional and federal voting rights acts, and federal civil rights litigation in federal court. EXCLUDES: routine administrative law, specific regulatory compliance, or criminal constitutional issues (criminal law category)."
    },
    
    "Product & Services Liability Law": {
        "Attorney Malpractice": "EXCLUSIVELY legal malpractice under state professional liability law and legal ethics rules. Covers: attorney negligence and breach of standard of care under state malpractice law, missed deadlines and statute of limitations violations, conflict of interest violations under state ethics rules, inadequate representation and competency failures, client trust account violations and commingling of funds, fee disputes and billing fraud under state fee arbitration procedures, breach of fiduciary duty by attorneys, and legal malpractice insurance coverage disputes. EXCLUDES: other professional malpractice, general negligence, or disciplinary proceedings (separate from civil liability).",
        
        "Defective Products": "SPECIFICALLY product liability under state tort law for physical injuries caused by defective consumer and commercial products. Limited to: design defect claims under consumer expectation or risk-utility analysis, manufacturing defect claims and quality control failures, failure to warn and inadequate instruction defect claims, strict product liability under Restatement of Torts Section 402A, product recall liability and post-sale duties to warn, mass tort and class action product litigation, pharmaceutical and medical device product liability, and product liability insurance coverage and bad faith claims. EXCLUDES: service liability (separate category), professional malpractice, or warranty claims without physical injury.",
        
        "Warranties": "EXCLUSIVELY product and service warranties under Uniform Commercial Code Article 2 and federal warranty law. Covers: express warranty creation and enforcement under UCC Section 2-313, implied warranty of merchantability under UCC Section 2-314, implied warranty of fitness for particular purpose under UCC Section 2-315, warranty disclaimer and limitation validity under UCC Section 2-316, Magnuson-Moss Warranty Act compliance and enforcement, breach of warranty remedies and damages, automobile lemon laws under state lemon law statutes, and warranty repair and replacement obligations. EXCLUDES: product liability with physical injury, service contracts, or general contract breaches.",
        
        "Consumer Protection and Fraud": "SPECIFICALLY consumer protection under federal and state consumer protection statutes. Limited to: deceptive and unfair trade practices under state consumer protection acts, consumer fraud and misrepresentation under state and federal law, telemarketing fraud and Telephone Consumer Protection Act violations, door-to-door sales and cooling-off period violations, identity theft and privacy violations under federal privacy laws, automobile dealer fraud and unfair practices, home improvement and contractor fraud, and consumer class action remedies and attorney fees. EXCLUDES: product liability, professional malpractice, or general business fraud."
    },
    
    "Intellectual Property Law": {
        "Copyright": "EXCLUSIVELY copyright protection under federal Copyright Act (17 USC 101-1511). Covers: copyright registration and ownership under Copyright Act Section 408-409, copyright infringement claims and fair use defenses under Section 107, Digital Millennium Copyright Act (DMCA) takedown procedures and safe harbor provisions, work for hire determinations under Section 101, copyright licensing and permissions, derivative works and compilation copyrights, copyright duration and renewal issues, and copyright litigation including preliminary injunctions and damages. EXCLUDES: trademark matters, patent issues, or trade secret protection.",
        
        "Patents": "SPECIFICALLY patent protection under federal Patent Act (35 USC 1-390). Limited to: patent applications and prosecution before USPTO under 35 USC 111-121, patent infringement and validity challenges under 35 USC 271, patent licensing and technology transfer agreements, patent portfolio management and maintenance, prior art searches and patentability analysis, international patent protection under Patent Cooperation Treaty, utility, design, and plant patent applications, and patent litigation including claim construction and damages. EXCLUDES: copyright protection, trademark registration, or trade secret matters.",
        
        "Trademarks": "EXCLUSIVELY trademark protection under federal Trademark Act (15 USC 1051-1141) and state trademark law. Covers: trademark registration and prosecution before USPTO under Trademark Act Section 1-23, trademark infringement and likelihood of confusion analysis, trademark dilution under federal and state dilution statutes, trademark licensing and assignment agreements, domain name disputes and cybersquatting under Anticybersquatting Consumer Protection Act, trademark opposition and cancellation proceedings before USPTO, international trademark protection under Madrid Protocol, and trademark litigation and enforcement. EXCLUDES: copyright matters, patent protection, or general business name disputes."
    },
    
    "Landlord/Tenant Law": {
        "General Landlord and Tenant Issues": "EXCLUSIVELY rental housing relationships under state landlord-tenant statutes and local housing codes. Covers: residential lease agreement preparation and interpretation under state landlord-tenant law, security deposit collection, handling, and return under state security deposit statutes, eviction proceedings including unlawful detainer actions under state eviction procedures, habitability and housing code compliance under state warranty of habitability, rent collection and rent control compliance under local rent stabilization ordinances, landlord and tenant rights and obligations under state residential landlord-tenant acts, housing discrimination under federal Fair Housing Act and state fair housing laws, and mobile home park regulation under state mobile home residency laws. EXCLUDES: commercial leasing (real estate law), homeowner association issues, or property ownership disputes."
    }
}

# Comprehensive Specialist Configurations
SPECIALIST_CONFIGURATIONS = {
    "Criminal Law": {
        "keywords": [
            "arrest", "arrested", "charged", "criminal", "crime", "police", "felony", 
            "misdemeanor", "drugs", "dui", "theft", "assault", "fraud", "jail", "prison",
            "prosecutor", "defendant", "guilty", "plea", "sentence", "parole", "probation",
            "convicted", "trial", "court", "judge", "jury", "warrant", "bail", "fine",
            "violation", "offense", "citation", "booking", "indictment", "arraignment",
            "hearing", "evidence", "testimony", "witness", "appeal", "sentencing",
            "criminal record", "background check", "expungement", "diversion", "pretrial",
            "detention", "custody", "interrogation", "confession", "search", "seizure"
        ],
        "legal_concepts": [
            "criminal liability", "criminal procedure", "constitutional rights", 
            "due process", "search and seizure", "Miranda rights", "plea bargaining",
            "criminal penalties", "criminal record", "legal defense", "prosecution",
            "burden of proof", "reasonable doubt", "probable cause", "Fourth Amendment",
            "Fifth Amendment", "Sixth Amendment", "right to counsel", "speedy trial",
            "double jeopardy", "self-incrimination", "criminal intent", "mens rea",
            "actus reus", "strict liability", "conspiracy", "accomplice liability"
        ],
        "case_examples": [
            "Defendant charged with felony drug possession requiring criminal defense strategy",
            "Individual arrested for DUI seeking representation for criminal proceedings",
            "Person facing white-collar fraud charges in federal criminal court",
            "Defendant requiring legal representation for assault charges and plea negotiations",
            "Individual needing criminal defense for theft allegations and trial preparation",
            "Person charged with domestic violence requiring immediate legal counsel",
            "Defendant facing multiple felony counts requiring comprehensive defense strategy",
            "Individual arrested on warrant seeking bail reduction and defense representation",
            "Person subject to criminal investigation seeking legal protection and advice",
            "Defendant appealing criminal conviction and seeking post-conviction relief"
        ]
    },
    
    "Immigration Law": {
        "keywords": [
            "deport", "deportation", "immigration", "visa", "citizenship", "green card", 
            "ice", "removal", "asylum", "refugee", "border", "undocumented", "daca",
            "naturalization", "permanent resident", "work permit", "entry", "uscis",
            "immigration court", "removal proceedings", "adjustment of status",
            "family petition", "employment authorization", "travel document",
            "consular processing", "waiver", "inadmissible", "overstay", "expired visa",
            "deportable", "priority date", "visa bulletin", "labor certification"
        ],
        "legal_concepts": [
            "immigration status", "removal proceedings", "immigration benefits",
            "visa applications", "citizenship eligibility", "asylum claims",
            "deportation defense", "immigration court", "USCIS procedures",
            "adjustment of status", "consular processing", "inadmissibility",
            "deportability", "relief from removal", "cancellation of removal",
            "withholding of removal", "Convention Against Torture", "U visa", "T visa",
            "VAWA self-petition", "registry", "section 245(i)", "unlawful presence"
        ],
        "case_examples": [
            "Individual facing removal proceedings requiring deportation defense",
            "Foreign national seeking asylum protection from persecution",
            "Person applying for permanent residence through family sponsorship",
            "Individual appealing denial of citizenship application",
            "Worker requiring legal assistance with employment-based visa application",
            "Person seeking cancellation of removal due to extreme hardship",
            "Individual applying for U visa as crime victim requiring legal representation",
            "Family member petitioning for relative's immigration status adjustment",
            "Person detained by ICE seeking bond and release from immigration custody",
            "Individual applying for asylum based on political persecution in home country"
        ]
    },
    
    "Family Law": {
        "keywords": [
            "divorce", "custody", "child support", "marriage", "separation", "alimony", 
            "adoption", "guardianship", "paternity", "visitation", "spousal support",
            "family court", "parenting time", "domestic relations", "marital property",
            "prenuptial", "postnuptial", "domestic violence", "restraining order",
            "modification", "contempt", "mediation", "collaborative divorce",
            "equitable distribution", "community property", "child welfare", "cps",
            "parental rights", "termination", "best interests", "joint custody"
        ],
        "legal_concepts": [
            "marital dissolution", "child welfare", "parental rights", 
            "domestic relations", "family court procedures", "child advocacy",
            "spousal maintenance", "custody arrangements", "adoption law",
            "guardianship proceedings", "paternity establishment", "child support guidelines",
            "best interests of child", "parental fitness", "domestic violence protection",
            "property division", "equitable distribution", "marital assets and debts",
            "parenting plans", "relocation", "jurisdiction", "interstate custody"
        ],
        "case_examples": [
            "Couple seeking legal divorce with contested child custody arrangements",
            "Parent requesting modification of child support due to changed circumstances",
            "Individual pursuing stepchild adoption requiring legal documentation",
            "Party disputing paternity and seeking court-ordered DNA testing",
            "Parent seeking emergency custody modification due to safety concerns",
            "Spouse filing for divorce with complex property division issues",
            "Individual seeking domestic violence protection order and emergency custody",
            "Grandparent pursuing guardianship of minor grandchildren",
            "Parent relocating with children requiring custody modification",
            "Individual establishing paternity to obtain parenting rights and responsibilities"
        ]
    },
    
    "Employment Law": {
        "keywords": [
            "fired", "employer", "workplace", "discrimination", "harassment", "wages", 
            "overtime", "wrongful termination", "sexual harassment", "disability", "job", "work",
            "employment", "labor", "employee", "boss", "supervisor", "hr", "benefits",
            "retaliation", "whistleblower", "hostile work environment", "accommodation",
            "family leave", "workers compensation", "unemployment", "severance",
            "non-compete", "confidentiality", "at-will employment", "collective bargaining",
            "union", "layoff", "demotion", "promotion", "performance evaluation"
        ],
        "legal_concepts": [
            "employment discrimination", "wrongful termination", "workplace rights",
            "labor law", "employment contracts", "workplace harassment",
            "wage and hour law", "workers' compensation", "employment benefits",
            "reasonable accommodation", "hostile work environment", "retaliation",
            "whistleblower protection", "family and medical leave", "at-will employment",
            "collective bargaining", "union rights", "employment classification",
            "independent contractor", "exempt vs non-exempt", "constructive discharge"
        ],
        "case_examples": [
            "Employee terminated in retaliation for reporting workplace safety violations",
            "Worker experiencing age and gender discrimination in promotion decisions",
            "Employee subjected to sexual harassment by supervisor requiring legal action",
            "Worker denied reasonable disability accommodation in workplace",
            "Employee denied overtime compensation despite working excessive hours",
            "Individual facing workplace retaliation after filing discrimination complaint",
            "Worker seeking family medical leave accommodation from resistant employer",
            "Employee challenging non-compete agreement restricting future employment",
            "Worker misclassified as independent contractor seeking employee benefits",
            "Employee experiencing constructive discharge due to intolerable working conditions"
        ]
    },
    
    "Personal Injury Law": {
        "keywords": [
            "accident", "injury", "medical malpractice", "car accident", "slip and fall", 
            "damages", "compensation", "negligence", "liability", "hospital", "doctor error",
            "injured", "hurt", "pain", "suffering", "medical bills", "insurance claim",
            "premises liability", "product liability", "wrongful death", "catastrophic injury",
            "brain injury", "spinal cord", "broken bones", "surgery", "rehabilitation",
            "settlement", "lawsuit", "personal injury attorney", "insurance adjuster"
        ],
        "legal_concepts": [
            "personal injury claims", "negligence law", "medical malpractice",
            "premises liability", "product liability", "insurance coverage",
            "damages assessment", "liability determination", "injury compensation",
            "pain and suffering", "economic damages", "non-economic damages",
            "comparative negligence", "contributory negligence", "statute of limitations",
            "burden of proof", "standard of care", "proximate cause", "strict liability",
            "punitive damages", "loss of consortium", "future medical expenses"
        ],
        "case_examples": [
            "Individual injured in motor vehicle collision seeking compensation for damages",
            "Person injured in slip and fall accident due to negligent premises maintenance",
            "Patient harmed by medical malpractice requiring professional liability claim",
            "Consumer injured by defective product seeking product liability compensation",
            "Individual suffering complications from misdiagnosed medical condition",
            "Victim of workplace accident seeking personal injury and workers' compensation",
            "Family pursuing wrongful death claim after fatal accident caused by negligence",
            "Person injured in construction accident requiring comprehensive legal representation",
            "Individual suffering catastrophic brain injury in vehicle accident",
            "Patient injured by defective medical device seeking manufacturer liability"
        ]
    },
    
    "Business/Corporate Law": {
        "keywords": [
            "business", "contract", "partnership", "corporation", "llc", "breach", 
            "partnership dispute", "shareholder", "merger", "acquisition", "competitor",
            "vendor", "client", "commercial", "enterprise", "company", "modeling agency",
            "talent agency", "service agreement", "professional services", "consultant",
            "contractor", "freelance", "agency", "modeling", "entertainment", "talent",
            "management", "representation", "booking", "gigs", "exposure", "portfolio",
            "commercial dispute", "business litigation", "corporate governance",
            "intellectual property", "trade secrets", "non-disclosure", "licensing",
            "franchise", "joint venture", "business formation", "corporate compliance"
        ],
        "legal_concepts": [
            "business law", "corporate governance", "commercial contracts",
            "business disputes", "corporate compliance", "business transactions",
            "partnership law", "contract law", "commercial litigation", "service contracts",
            "professional agreements", "agency agreements", "entertainment contracts",
            "modeling contracts", "talent representation", "commercial fraud",
            "contract performance", "breach of contract", "contract cancellation",
            "business formation", "corporate structure", "fiduciary duties", "piercing corporate veil",
            "business torts", "unfair competition", "trade secret protection"
        ],
        "case_examples": [
            "Business partners disputing partnership agreement terms and profit distribution",
            "Company facing breach of contract claims from commercial vendor",
            "Corporation requiring legal assistance with merger and acquisition transaction",
            "Business owner discovering competitor using proprietary trade secrets",
            "Individual with modeling agency contract dispute regarding service delivery",
            "Professional service provider facing contract performance disputes",
            "Entertainment industry professional requiring contract review and negotiation",
            "Startup seeking legal guidance on business formation and corporate structure",
            "Company defending against commercial litigation and seeking damages",
            "Business owner pursuing collection of unpaid invoices and contract enforcement",
            "Corporation facing shareholder dispute over corporate governance issues",
            "Franchise owner disputing franchise agreement terms with franchisor"
        ]
    },
    
    "Intellectual Property Law": {
        "keywords": [
            "copyright", "trademark", "patent", "intellectual property", "logo", 
            "brand", "content", "copied", "copying", "infringement", "stolen", "plagiarism",
            "invention", "creative", "original", "ip", "licensing", "royalty",
            "trade secret", "proprietary", "counterfeit", "piracy", "DMCA",
            "trademark registration", "patent application", "copyright registration",
            "fair use", "derivative work", "patent prosecution", "trademark opposition"
        ],
        "legal_concepts": [
            "intellectual property rights", "copyright protection", "patent law",
            "trademark registration", "IP infringement", "licensing agreements",
            "trade secrets", "IP litigation", "creative works protection",
            "fair use", "derivative works", "trademark dilution", "patent prosecution",
            "prior art", "novelty", "non-obviousness", "trademark distinctiveness",
            "copyright ownership", "work for hire", "IP assignment", "patent validity",
            "trademark likelihood of confusion", "copyright fair use defense"
        ],
        "case_examples": [
            "Creator discovering unauthorized use of copyrighted material requiring enforcement action",
            "Business owner facing trademark infringement claims from competitor",
            "Inventor seeking patent protection for new technological innovation",
            "Company pursuing trade secret misappropriation claim against former employee",
            "Artist requiring copyright registration and licensing agreement assistance",
            "Software company defending against patent infringement allegations",
            "Brand owner pursuing trademark opposition against confusingly similar mark",
            "Content creator seeking DMCA takedown enforcement and damages recovery",
            "Inventor challenging patent rejection and seeking patent prosecution assistance",
            "Company licensing intellectual property and requiring licensing agreement review"
        ]
    },
    
    "Real Estate Law": {
        "keywords": [
            "real estate", "property", "house", "home", "mortgage", "foreclosure",
            "deed", "title", "closing", "inspection", "appraisal", "zoning",
            "real property", "land", "residential", "commercial property",
            "landlord", "tenant", "lease", "rent", "eviction", "easement",
            "boundary dispute", "survey", "HOA", "condominium", "construction",
            "purchase agreement", "seller disclosure", "title insurance", "escrow"
        ],
        "legal_concepts": [
            "real estate transactions", "property law", "real estate contracts",
            "property disputes", "real estate closings", "property rights",
            "foreclosure proceedings", "title issues", "property development",
            "zoning law", "land use", "eminent domain", "adverse possession",
            "easements", "covenants", "deed restrictions", "property taxation",
            "construction law", "mechanic's liens", "quiet title actions", "survey disputes",
            "environmental contamination", "property disclosure", "real estate agency law"
        ],
        "case_examples": [
            "Homeowner facing foreclosure proceedings requiring legal defense",
            "Property buyer discovering title defects requiring legal resolution",
            "Real estate transaction delayed due to contract disputes and inspection issues",
            "Property owners disputing boundary lines with neighboring landowners",
            "Commercial property developer facing zoning and land use restrictions",
            "Homeowner challenging property tax assessment and seeking reduction",
            "Property owner dealing with construction defects and contractor disputes",
            "Real estate investor pursuing quiet title action to resolve ownership disputes",
            "Condominium owner facing HOA assessment and governance disputes",
            "Commercial tenant facing lease dispute and potential eviction proceedings"
        ]
    },
    
    "Product & Services Liability Law": {
        "keywords": [
            "defective", "product", "recall", "contamination", "malfunction", "warranty",
            "consumer protection", "false advertising", "attorney malpractice",
            "service failure", "product safety", "consumer rights", "fraud",
            "misrepresentation", "breach of warranty", "design defect", "manufacturing defect",
            "failure to warn", "strict liability", "consumer fraud", "deceptive practices",
            "professional negligence", "malpractice insurance", "product liability insurance"
        ],
        "legal_concepts": [
            "product liability", "consumer protection law", "warranty law",
            "product safety", "professional malpractice", "consumer fraud",
            "defective products", "service liability", "consumer rights",
            "strict liability", "negligence", "breach of warranty", "design defects",
            "manufacturing defects", "failure to warn", "professional negligence",
            "consumer protection statutes", "deceptive trade practices", "lemon laws",
            "product recall liability", "mass tort litigation", "class action lawsuits"
        ],
        "case_examples": [
            "Consumer injured by defective product requiring product liability claim",
            "Individual harmed by contaminated food product seeking compensation",
            "Client pursuing attorney malpractice claim for missed legal deadlines",
            "Consumer deceived by false advertising requiring consumer protection action",
            "Person harmed by recalled product that was not properly warned about defects",
            "Patient injured by defective medical device seeking manufacturer liability",
            "Consumer facing financial loss due to professional service negligence",
            "Individual pursuing warranty claim against manufacturer for product failure",
            "Consumer participating in class action lawsuit against defective product manufacturer",
            "Individual seeking damages for professional malpractice and breach of fiduciary duty"
        ]
    },
    
    "Bankruptcy, Finances, & Tax Law": {
        "keywords": [
            "bankruptcy", "debt", "creditor", "collection", "tax", "irs", "audit",
            "property tax", "income tax", "consumer credit", "chapter 7", "chapter 13",
            "financial", "money", "payment", "owe", "owing", "bill", "bills",
            "foreclosure", "repossession", "garnishment", "levy", "lien",
            "discharge", "trustee", "automatic stay", "means test", "tax lien",
            "tax levy", "offer in compromise", "installment agreement", "tax penalty"
        ],
        "legal_concepts": [
            "bankruptcy law", "debt relief", "tax law", "financial restructuring",
            "creditor rights", "tax compliance", "debt collection", "financial planning",
            "tax disputes", "bankruptcy proceedings", "automatic stay", "discharge",
            "exemptions", "liquidation", "reorganization", "tax assessment",
            "tax appeal", "offer in compromise", "installment agreement", "collection actions",
            "preference payments", "fraudulent transfers", "reaffirmation agreements", "tax liens"
        ],
        "case_examples": [
            "Individual filing Chapter 7 bankruptcy for overwhelming debt relief",
            "Debtor facing aggressive creditor collection actions requiring legal protection",
            "Taxpayer undergoing IRS audit requiring professional tax representation",
            "Property owner disputing tax assessment and seeking property tax reduction",
            "Small business owner requiring tax planning and compliance assistance",
            "Person seeking Chapter 13 bankruptcy to save home from foreclosure",
            "Individual challenging IRS tax lien and seeking resolution options",
            "Debtor defending against creditor garnishment and seeking bankruptcy protection",
            "Business owner facing tax levy and seeking immediate release of assets",
            "Individual negotiating offer in compromise with IRS for tax debt settlement"
        ]
    },
    
    "Government & Administrative Law": {
        "keywords": [
            "social security", "disability", "benefits", "government", "administrative", 
            "veterans", "unemployment", "medicaid", "medicare", "denied", "claim", "appeal",
            "agency", "federal", "state", "public", "governmental", "va", "irs", "uscis",
            "department", "bureau", "commission", "regulatory", "compliance", "license suspension",
            "hearing", "administrative law judge", "due process", "regulatory enforcement",
            "government contract", "public benefits", "administrative review", "agency decision"
        ],
        "legal_concepts": [
            "administrative law", "government benefits", "administrative procedures",
            "regulatory compliance", "government agencies", "administrative appeals",
            "public law", "government services", "administrative hearings", "federal agencies",
            "state agencies", "regulatory enforcement", "government licensing",
            "public benefits", "administrative review", "due process", "substantial evidence",
            "scope of review", "exhaustion of remedies", "judicial review", "agency rulemaking",
            "administrative adjudication", "government liability", "sovereign immunity"
        ],
        "case_examples": [
            "Individual appealing denial of Social Security disability benefits determination",
            "Veteran challenging reduction of VA benefits requiring administrative appeal", 
            "Person denied unemployment benefits seeking administrative review",
            "Individual appealing Medicare coverage denial through administrative process",
            "Professional facing license suspension by regulatory agency requiring defense",
            "Business owner appealing regulatory agency enforcement action",
            "Individual challenging government agency benefit determination",
            "Person seeking veterans benefits for service-connected disability compensation",
            "Individual appealing Social Security retirement benefits calculation error",
            "Professional challenging occupational licensing board disciplinary action",
            "Business facing regulatory compliance investigation and enforcement action",
            "Individual seeking administrative appeal of government benefit overpayment determination"
        ]
    },
    
    "Wills, Trusts, & Estates Law": {
        "keywords": [
            "will", "trust", "estate", "probate", "inheritance", "beneficiary", "executor",
            "power of attorney", "living will", "advance directive", "heir", "inherit",
            "estate planning", "testament", "legacy", "administration", "conservatorship",
            "guardianship", "fiduciary", "asset protection", "estate tax", "gift tax",
            "trust administration", "will contest", "undue influence", "capacity",
            "probate court", "estate assets", "estate debts", "intestate", "testate"
        ],
        "legal_concepts": [
            "estate planning", "probate law", "trust administration", "estate law",
            "inheritance law", "will contests", "estate administration", "fiduciary duties",
            "estate taxation", "trust law", "asset protection", "succession planning",
            "testamentary capacity", "undue influence", "fraud", "gift and estate tax",
            "charitable giving", "business succession", "family wealth preservation",
            "intestate succession", "elective share", "homestead exemption", "family allowance"
        ],
        "case_examples": [
            "Family member contesting will due to suspicious circumstances and undue influence",
            "Individual establishing trust for minor children and estate planning purposes",
            "Executor facing complex probate administration with contested inheritance claims",
            "Business owner requiring comprehensive estate planning for asset protection",
            "Family member seeking power of attorney for incapacitated relative",
            "Beneficiary challenging trust administration and seeking fiduciary accountability",
            "Person establishing living trust to avoid probate and protect family assets",
            "Individual planning charitable giving strategy and tax-efficient estate transfer",
            "Family pursuing conservatorship proceedings for incapacitated elderly relative",
            "Estate administrator dealing with complex estate assets and creditor claims"
        ]
    },
    
    "Landlord/Tenant Law": {
        "keywords": [
            "landlord", "tenant", "lease", "rent", "eviction", "deposit", "repairs",
            "rental", "apartment", "housing", "mold", "habitability", "security deposit",
            "renter", "renting", "tenancy", "rental property", "breach of lease",
            "rent control", "housing code", "uninhabitable", "constructive eviction",
            "rent increase", "notice to quit", "unlawful detainer", "rental agreement",
            "housing discrimination", "fair housing", "tenant screening", "rental inspection"
        ],
        "legal_concepts": [
            "landlord-tenant law", "rental agreements", "housing law", "tenant rights",
            "habitability standards", "eviction procedures", "rental disputes",
            "housing regulations", "lease agreements", "property management",
            "warranty of habitability", "constructive eviction", "retaliatory eviction",
            "rent control", "security deposits", "landlord liability", "tenant remedies",
            "fair housing law", "housing discrimination", "reasonable accommodation in housing",
            "landlord's duty to mitigate damages", "tenant's right to quiet enjoyment"
        ],
        "case_examples": [
            "Tenant facing eviction proceedings requiring legal defense",
            "Renter pursuing security deposit return from non-responsive landlord",
            "Tenant dealing with habitability issues and landlord negligence",
            "Landlord pursuing eviction for lease violations and non-payment",
            "Renter challenging improper rent increase under rent control regulations",
            "Tenant seeking damages for uninhabitable conditions and health hazards",
            "Landlord defending against discrimination claims in rental practices",
            "Renter facing retaliatory eviction after reporting housing code violations",
            "Tenant seeking reasonable accommodation for disability under fair housing law",
            "Landlord pursuing damages for breach of lease and property damage by tenant"
        ]
    }
}

def get_legal_area_definition(area: str) -> str:
    """Get the definition for a specific legal area"""
    return LEGAL_AREA_DEFINITIONS.get(area, f"Legal matters primarily governed by {area} statutes, regulations, and legal principles.")

def get_subcategory_explanation(area: str, subcategory: str) -> str:
    """Get detailed explanation for a specific subcategory"""
    area_subcategories = SUBCATEGORY_EXPLANATIONS.get(area, {})
    return area_subcategories.get(subcategory, f"{subcategory} matters within {area} practice area.")

def get_specialist_config(area: str) -> dict:
    """Get configuration for a specific legal area"""
    return SPECIALIST_CONFIGURATIONS.get(area, {})

def get_all_legal_areas() -> list:
    """Get list of all configured legal areas"""
    return list(SPECIALIST_CONFIGURATIONS.keys())

def get_keywords_for_area(area: str) -> list:
    """Get keywords for a specific legal area"""
    config = SPECIALIST_CONFIGURATIONS.get(area, {})
    return config.get("keywords", [])

def get_legal_concepts_for_area(area: str) -> list:
    """Get legal concepts for a specific legal area"""
    config = SPECIALIST_CONFIGURATIONS.get(area, {})
    return config.get("legal_concepts", [])

def get_case_examples_for_area(area: str) -> list:
    """Get case examples for a specific legal area"""
    config = SPECIALIST_CONFIGURATIONS.get(area, {})
    return config.get("case_examples", [])

def get_all_subcategory_explanations() -> dict:
    """Get all subcategory explanations"""
    return SUBCATEGORY_EXPLANATIONS

def validate_configuration() -> dict:
    """Validate that all configurations are complete"""
    validation_results = {}
    
    for area, config in SPECIALIST_CONFIGURATIONS.items():
        results = {
            "has_definition": area in LEGAL_AREA_DEFINITIONS,
            "has_subcategory_explanations": area in SUBCATEGORY_EXPLANATIONS,
            "keywords_count": len(config.get("keywords", [])),
            "concepts_count": len(config.get("legal_concepts", [])),
            "examples_count": len(config.get("case_examples", [])),
            "is_valid": True
        }
        
        # Set validity based on minimum requirements
        if (results["keywords_count"] < 15 or 
            results["concepts_count"] < 8 or 
            results["examples_count"] < 8 or
            not results["has_definition"] or
            not results["has_subcategory_explanations"]):
            results["is_valid"] = False
            
        validation_results[area] = results
    
    return validation_results

# Configuration metadata
CONFIG_VERSION = "1.0.0"
CONFIG_LAST_UPDATED = "2024-07-29"
TOTAL_LEGAL_AREAS = len(SPECIALIST_CONFIGURATIONS)
TOTAL_SUBCATEGORIES = sum(len(SUBCATEGORY_EXPLANATIONS.get(area, {})) for area in SPECIALIST_CONFIGURATIONS.keys())