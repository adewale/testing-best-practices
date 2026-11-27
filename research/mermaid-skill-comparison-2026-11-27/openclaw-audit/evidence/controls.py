"""Apply one replayable hypothetical only inside this lane's scratch checkout."""
from pathlib import Path
import subprocess,sys
L=Path(__file__).resolve().parent.parent
work=L/'scratch'/'control'; mode=sys.argv[1]
if Path.cwd().resolve()!=work: raise ValueError('run from scratch/control')
def change(path, old,new):
 p=work/path
 base=subprocess.check_output(['git','show','HEAD:'+path],text=True)
 if base.count(old)!=1: raise ValueError(path)
 p.write_text(base.replace(old,new))
 (L/'evidence'/(mode+'.patch')).write_bytes(subprocess.check_output(['git','diff','--',path]))
 print(path, mode)
if mode.startswith('cli-'):
 old="""    const results = args.positional.map((file, index) => {
      try {
        const src = readSourceArg(file)
        const warnings = renderConfigWarningsForMermaid(src, formatOptions)
        emitConfigWarnings(warnings, `am render ${file}`)
        const rendered = renderSourceToFormatWithReceipt(src, format, reportingConfigDiagnosticsOnce(formatOptions, warnings))
        return { index, file, ok: true, output: rendered.output, receipt: rendered.receipt, warnings }
      } catch (e) {
        return {
          index,
          file,
          ok: false,
          error: e instanceof CliArgumentError ? { code: 'ARG', message: e.message } : cliStructuredRenderFailure(e).error,
        }
      }
    })"""
 new=old.replace('const results = args.positional.map((file, index) => {','const results = []\n    for (const [index, file] of args.positional.entries()) {').replace('return { index, file, ok: true, output: rendered.output, receipt: rendered.receipt, warnings }','results.push({ index, file, ok: true, output: rendered.output, receipt: rendered.receipt, warnings })').replace('        return {\n','        results.push({\n').replace('        }\n      }\n    })','        })\n'+('        break\n' if mode=='cli-fault' else '')+'      }\n    }')
 assert mode in ('cli-fault','cli-permitted')
 change('src/cli/index.ts',old,new)
elif mode=='css-fault':
 old='  --accent: #1B6E52;'
 change('website/source/assets/styles.css',old,'  --brand-pine: var(--accent);\n'+old)
elif mode=='css-permitted':
 change('website/source/assets/styles.css','  --brand-pine: #6FC2A2;', '  --brand-pine: rgb(111 194 162);')
else: raise ValueError(mode)
