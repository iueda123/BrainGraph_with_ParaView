getShortNameFromLongName <- function(long_NIDP_names){

  # 脳領域名から短縮名へのマッピングテーブルを作成
  # 領域群の頭文字 + 識別番号の形式（例: T1, F1, O1など）

  region_mapping <- list(
  

    
    # Temporal領域 (T)
    "bankssts" = "T1",
    "entorhinal" = "T2",
    "fusiform" = "T3",
    "inferiortemporal" = "T4",
    "middletemporal" = "T5",
    "superiortemporal" = "T6",
    "temporalpole" = "T7",
    "transversetemporal" = "T8",

    # Limbic System領域 (L)
    "caudalanteriorcingulate" = "L1", # これが caudよりも前にあると正しく探し出してもらえない
    "isthmuscingulate" = "L2",
    "parahippocampal" = "L3", # これが palよりも前にあると正しく探し出してもらえない
    "posteriorcingulate" = "L4",
    "rostralanteriorcingulate" = "L5",
    "hippo" = "L6",
    "amyg" = "L7",
    "accumb" = "L8",

    # Frontal領域 (F)
    "caudalmiddlefrontal" = "F1", # これが caudよりも前にあると正しく探し出してもらえない
    "lateralorbitofrontal" = "F2",
    "medialorbitofrontal" = "F3",
    "parsopercularis" = "F4",
    "parsorbitalis" = "F5",
    "parstriangularis" = "F6",
    "precentral" = "F7",
    "rostralmiddlefrontal" = "F8",
    "superiorfrontal" = "F9",
    "frontalpole" = "F10",

    # Parietal領域 (P)
    "inferiorparietal" = "P1",
    "paracentral" = "P2",
    "postcentral" = "P3",
    "precuneus" = "P4",  # これがcuneusよりも前にあると正しく探し出してもらえない
    "superiorparietal" = "P5",
    "supramarginal" = "P6",

    # Occipital領域 (O)
    "cuneus" = "O1",
    "lateraloccipital" = "O2",
    "lingual" = "O3",
    "pericalcarine" = "O4",

    # Insula領域 (I)
    "insula" = "I1",

     # Thalamus & Basal Ganglia (B)
    "thal" = "B1",
    "caud" = "B2", 
    "put" = "B3",
    "pal" = "B4",

    # Ventricle (V)
    "LatVent" = "V1"
  )

  # 短縮名を格納するベクトルを初期化
  short_NIDP_names <- character(length(long_NIDP_names))

  # 各長い名前に対して短縮名を検索
  for (i in seq_along(long_NIDP_names)) {
    long_name <- long_NIDP_names[i]
    short_name <- NA

    # マッピングテーブルの各キーワードをチェック
    for (keyword in names(region_mapping)) {
      if (grepl(keyword, long_name, fixed = FALSE)) {
        short_name <- region_mapping[[keyword]]
        break
      }
    }

    # 短縮名が見つからなかった場合は元の名前を使用
    if (is.na(short_name)) {
      short_NIDP_names[i] <- long_name
      warning(paste("No mapping found for:", long_name))
    } else {
      short_NIDP_names[i] <- short_name
    }
  }

  return(short_NIDP_names)
}

