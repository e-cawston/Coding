
gasmet_process <- function (
    wd = NA,
    process.file.list = FALSE,
    save.concat = FALSE,
    use.temp = TRUE,
    print.plots = FALSE,
    save.plots = TRUE,
    save.results = TRUE
) {
  
  
  
  if (!is.na(wd)) {
    setwd(wd)
  } else {
    setwd(choose.dir())
  }
  
  if (process.file.list) {
    
    file_table <- read.table(
      file.choose(),
      header = TRUE,
      sep = "\t",
      stringsAsFactors = FALSE
    )
    
  } else {
    
    file_list <- list.files(
      path = ".",
      pattern = "\\.TXT$"
    )
    
    splits <- strsplit(file_list, "[_.]")
    
    file_table <- data.frame(
      file.name = file_list,
      Location = sapply(splits, `[`, 1),
      Rep = sapply(splits, `[`, 2),
      stringsAsFactors = FALSE
    )
  }
  
  message("Processing ", nrow(file_table), " files")
  
  concat_files <- data.frame(
    Location = character(),
    Rep = character(),
    Date = as.Date(character()),
    Raw.Data.Location = character(),
    Time = character(),
    Carbon.Dioxide = numeric(),
    Nitrous.Oxide = numeric(),
    stringsAsFactors = FALSE
  )
  
  for (i in seq_len(nrow(file_table))) {
    
    file <- file_table$file.name[i]
    table <- read.table(file, header = TRUE, sep = "\t")
    
    if (!all(c("Date", "Time",
               "Carbon.dioxide.CO2",
               "Nitrous.oxide.N2O") %in% names(table))) {
      warning("Columns missing in ", file, "; skipped")
      next
    }
    
    include <- TRUE
    
    if (nrow(table) != 8) {
      ans <- toupper(readline(
        paste0("File ", file,
               " does not have 8 lines. Include? (Y/N): ")
      ))
      include <- ans == "Y"
      message(file, " included.")
      
    }
    
    if (include) {
      temp <- data.frame(
        Location = file_table$Location[i],
        Rep = file_table$Rep[i],
        Date = table$Date,
        Raw.Data.Location = file,
        Time = table$Time,
        Carbon.Dioxide = table$Carbon.dioxide.CO2,
        Nitrous.Oxide = table$Nitrous.oxide.N2O
      )
      concat_files <- rbind(concat_files, temp)
    }
  }
  
  concat_files$Time <- as.numeric(lubridate::hms(concat_files$Time))
  
  message(length(unique(concat_files$Rep)), " reps processed")
  
  if (save.concat) {
    openxlsx::write.xlsx(
      concat_files,
      paste0(unique(concat_files$Location),
             "_Gasmet_Measurements.xlsx")
    )
  }
  
  calc_measures <- concat_files |>
    dplyr::mutate(
      CO2.Used = NA,
      N2O.Used = NA
    ) |>
    dplyr::group_by(Rep) |>
    dplyr::mutate(Rep.Number = dplyr::row_number()) |>
    dplyr::ungroup()
  
  if (use.temp) {
    repeat {
      ans <- readline(
        "Input temperature values for reps. Enter 1 to supply a tab separated file, enter 2 to give individual values for each rep (1/2): "
      )
      if (ans == "1") {
        temperatures <- read.table(file.choose(),
                                   stringsAsFactors = FALSE)
        temp.type <- "FILE"
        break
      }
      if (ans == "2") {
        temp.type <- "INDIV"
        break
      }
    }
  }
  
  if (save.plots && !dir.exists("Plots")) {
    dir.create("Plots")
  }
  
  summary_output <- list()
  
  for (rep in unique(calc_measures$Rep)) {
    
    temp <- calc_measures[calc_measures$Rep == rep, ]
    
    model.co2.1 <- lm(Carbon.Dioxide ~ Time, data = temp)
    temp$CO2.Used <- abs(rstudent(model.co2.1)) <= 3
    calc_measures$CO2.Used[calc_measures$Rep == rep] <- temp$CO2.Used
    
    clean.co2 <- temp[temp$CO2.Used, ]
    if (nrow(clean.co2) < 2) next
    model.co2.2 <- lm(Carbon.Dioxide ~ Time, data = clean.co2)
    
    model.n2o.1 <- lm(Nitrous.Oxide ~ Time, data = temp)
    temp$N2O.Used <- abs(rstudent(model.n2o.1)) <= 3
    calc_measures$N2O.Used[calc_measures$Rep == rep] <- temp$N2O.Used
    
    clean.n2o <- temp[temp$N2O.Used, ]
    if (nrow(clean.n2o) < 2) next
    model.n2o.2 <- lm(Nitrous.Oxide ~ Time, data = clean.n2o)
    
    if (use.temp) {
      if (temp.type == "FILE") {
        temp.value <- temperatures[temperatures[[1]] == rep, 2]
        if (length(temp.value) != 1)
          stop("Temperature missing or duplicated for rep ", rep)
      } else {
        temp.value <- as.numeric(
          readline(paste("Enter Celsius for ", rep, ": "))
        )
      }
      va <- 0.0224 * (273.15 / (temp.value + 273.15))
    } else {
      va <- 0.0224
    }
    
    v <- 0.00967
    A <- 0.0314
    
    CO2_flux <- coef(model.co2.2)[2] * ((v / va) / A)
    N2O_flux <- coef(model.n2o.2)[2] * ((v / va) / A)
    
    summary_output[[rep]] <- data.frame(
      Rep = rep,
      CO2_Slope = coef(model.co2.2)[2],
      CO2_Intercept = coef(model.co2.2)[1],
      CO2_R2_Original = summary(model.co2.1)$r.squared,
      CO2_R2_Clean = summary(model.co2.2)$r.squared,
      CO2_N_used = nrow(clean.co2),
      CO2_N_total = nrow(temp),
      CO2_Flux = CO2_flux,
      N2O_Slope = coef(model.n2o.2)[2],
      N2O_Intercept = coef(model.n2o.2)[1],
      N2O_R2_Original = summary(model.n2o.1)$r.squared,
      N2O_R2_Clean = summary(model.n2o.2)$r.squared,
      N2O_N_used = nrow(clean.n2o),
      N2O_N_total = nrow(temp),
      N2O_Flux = N2O_flux
    )
    
    if (print.plots || save.plots) {
      
      p1 <- ggplot2::ggplot(temp,
                            ggplot2::aes(Time, Carbon.Dioxide,
                       colour = CO2.Used)) +
        ggplot2::geom_point() +
        ggplot2::geom_abline(intercept = coef(model.co2.2)[1],
                    slope = coef(model.co2.2)[2]) +
        ggplot2::labs(title = paste(rep, "CO2"))
      
      p2 <- ggplot2::ggplot(temp,
                                     ggplot2::aes(Time, Nitrous.Oxide,
                       colour = N2O.Used)) +
        ggplot2::geom_point() +
        ggplot2::geom_abline(intercept = coef(model.n2o.2)[1],
                    slope = coef(model.n2o.2)[2]) +
        ggplot2::labs(title = paste(rep, "N2O"))
      
      if (print.plots) {
        print(p1); print(p2)
      }
      
      if (save.plots) {
        ggplot2::ggsave(paste0("Plots/", rep, "_CO2.png"), p1,
               width = 8, height = 6, dpi = 300)
        ggplot2::ggsave(paste0("Plots/", rep, "_N2O.png"), p2,
               width = 8, height = 6, dpi = 300)
      }
    }
  }
  
  summary_output <- do.call(rbind, summary_output)
  
  if (save.results) {
    openxlsx::write.xlsx(
      summary_output,
      paste0(unique(concat_files$Location),
             "_Flux_Values.xlsx")
    )
    openxlsx::write.xlsx(
      calc_measures,
      paste0(unique(concat_files$Location),
             "_Flux_Check.xlsx")
    )
    message("Results saved.")
  }
  
  invisible(list(
    summary = summary_output,
    data = calc_measures
  ))
  
  message("Function finished.")
}